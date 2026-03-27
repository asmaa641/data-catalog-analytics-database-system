import requests
import mysql.connector
import re
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# helper functions for cleaning, parsing, and extracting structured data from raw input

# extracts a phone number from a text string using regex
def extract_phone(text):
    if not text:
        return None
    match = re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', text)
    return match.group() if match else None

# converts ISO date string into a python date object
def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "")).date()
    except:
        return None

# cleans a value into a safe trimmed string with optional max length
def safe_str(val, max_len=None):
    if not val:
        return None
    val = str(val).strip()
    if not val:
        return None
    return val[:max_len] if max_len else val


# ckan specific extractions for fields that arent at the top level

# determines the file format of a resource from available fields
def extract_format(r):
    for key in ["format", "mimetype", "mimetype_inner"]:
        val = r.get(key)
        if val and str(val).strip():
            return str(val).strip()
    return "UNKNOWN"

# retrieves dataset access level from CKAN extras (defaults to public)
def extract_access_level(d):
    for e in d.get("extras", []):
        if e.get("key") == "accessLevel":
            return e.get("value")
    return "public"

# converts textual frequency (e.g. monthly) into number of days
def extract_frequency(value):
    if not value:
        return None

    value = value.lower()

    mapping = {
        "daily": 1,
        "weekly": 7,
        "monthly": 30,
        "quarterly": 90,
        "yearly": 365
    }

    for k in mapping:
        if k in value:
            return mapping[k]

    return None

# extracts update frequency from dataset extras using keyword matching
def extract_frequency_from_extras(d):
    for e in d.get("extras", []):
        key = (e.get("key") or "").lower()
        val = e.get("value")

        if "frequency" in key:
            return extract_frequency(val)

    return None  # VALID if missing

# gets the best available homepage URL using priority fallback logic
def extract_homepage(d):
    # best source is the landingPage
    for e in d.get("extras", []):
        if e.get("key") == "landingPage":
            return e.get("value")

    # fallback
    if d.get("url"):
        return d.get("url")

    for r in d.get("resources", []):
        if r.get("url"):
            return r.get("url")

    return None


#  DB connecting

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor = conn.cursor()

# setting up API endpoint and pagination parameters for crawling

url = "https://catalog.data.gov/api/3/action/package_search"

rows = 50
start = 0
max_pages = 100

# loops through paginated API results to fetch datasets
for page in range(max_pages):
    print(f"Processing page {page + 1}")

    response = requests.get(url, params={"rows": rows, "start": start})
    data = response.json()
    datasets = data["result"]["results"]

    if not datasets:
        break

    for d in datasets:

        # organizatiton
        # inserts new organization or retrieves existing organization ID from database
        org = d.get("organization", {})
        org_name = safe_str(org.get("title"), 255)

        if not org_name:
            continue

        cursor.execute(
            "SELECT Organization_ID FROM Publishing_Organization WHERE Name=%s",
            (org_name,)
        )
        result = cursor.fetchone()

        if result:
            org_id = result[0]
        else:
            cursor.execute("""
                INSERT INTO Publishing_Organization
                (Name, Email, Phone, Organization_type, Description)
                VALUES (%s,%s,%s,%s,%s)
            """, (
                org_name,
                safe_str(d.get("maintainer_email"), 100),
                extract_phone(d.get("maintainer")),
                safe_str(org.get("type"), 100),
                safe_str(org.get("description"), 2000)
            ))
            org_id = cursor.lastrowid

        # dataset
        # inserts or updates dataset records with extracted metadata
        dataset_name = safe_str(d.get("title"), 200)

        cursor.execute(
            "SELECT Dataset_ID FROM Dataset WHERE Name=%s AND Organization_ID=%s",
            (dataset_name, org_id)
        )
        existing = cursor.fetchone()

        topic = None
        if d.get("groups"):
            topic = safe_str(d["groups"][0].get("title"), 100)

        values = (
            dataset_name,
            safe_str(d.get("notes"), 2000),
            topic,
            extract_access_level(d), 
            safe_str(d.get("maintainer"), 255),
            safe_str(d.get("license_title"), 255),
            parse_date(d.get("metadata_created")),
            parse_date(d.get("metadata_modified")),
            parse_date(d.get("metadata_created")),
            parse_date(d.get("metadata_modified")),
            extract_frequency_from_extras(d), 
            safe_str(extract_homepage(d), 500), 
            safe_str(d.get("id"), 255),
            org_id
        )

        if existing:
            dataset_id = existing[0]

            cursor.execute("""
                UPDATE Dataset SET
                    Description=%s,
                    Topic=%s,
                    Access_Level=%s,
                    Maintainer=%s,
                    License=%s,
                    Metadata_creation_date=%s,
                    Metadata_update_date=%s,
                    Data_First_published=%s,
                    Data_last_modified=%s,
                    Data_Update_Frequency=%s,
                    Homepage_URL=%s,
                    Identifier=%s
                WHERE Dataset_ID=%s
            """, (
                values[1], values[2], values[3], values[4], values[5],
                values[6], values[7], values[8], values[9], values[10],
                values[11], values[12],
                dataset_id
            ))

        else:
            cursor.execute("""
                INSERT INTO Dataset (
                    Name, Description, Topic, Access_Level, Maintainer, License,
                    Metadata_creation_date, Metadata_update_date,
                    Data_First_published, Data_last_modified,
                    Data_Update_Frequency, Homepage_URL, Identifier,
                    Organization_ID
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, values)

            dataset_id = cursor.lastrowid

        # resources
        #inserts or updates dataset resource files and their formats
        for r in d.get("resources", []):
            resource_url = safe_str(r.get("url"), 1000)
            fmt = safe_str(extract_format(r), 1000)

            if not resource_url:
                continue

            cursor.execute(
                "SELECT Resource_ID FROM File_Resource WHERE URL=%s AND Dataset_ID=%s",
                (resource_url, dataset_id)
            )
            existing_resource = cursor.fetchone()

            if existing_resource:
                cursor.execute("""
                    UPDATE File_Resource
                    SET Format=%s
                    WHERE Resource_ID=%s
                """, (fmt, existing_resource[0]))
            else:
                cursor.execute("""
                    INSERT INTO File_Resource (Format, URL, Dataset_ID)
                    VALUES (%s,%s,%s)
                """, (fmt, resource_url, dataset_id))

        # tags
        # inserts tags and links them to datasets while avoiding duplicates
        for t in d.get("tags", []):
            tag_name = safe_str(t.get("name"), 100)

            if not tag_name:
                continue

            cursor.execute("SELECT Tag_ID FROM Tag WHERE Tag_Name=%s", (tag_name,))
            tag_result = cursor.fetchone()

            if tag_result:
                tag_id = tag_result[0]
            else:
                cursor.execute("INSERT INTO Tag (Tag_Name) VALUES (%s)", (tag_name,))
                tag_id = cursor.lastrowid

            cursor.execute("""
                SELECT * FROM Dataset_Tag WHERE Dataset_ID=%s AND Tag_ID=%s
            """, (dataset_id, tag_id))

            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO Dataset_Tag (Dataset_ID, Tag_ID)
                    VALUES (%s,%s)
                """, (dataset_id, tag_id))

    start += rows # moves to the next page of API results

# Commits all changes and safely closes database connection
conn.commit()
cursor.close()
conn.close()

print("Finished 100 pages successfully")

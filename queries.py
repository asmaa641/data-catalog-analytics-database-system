def register_user(conn):
    cursor = conn.cursor()
    try:
        email = input("Email: ").strip()
        username = input("Username: ").strip()
        gender = input("Gender: ").strip()
        age = input("Age: ").strip()
        birthdate = input("Birthdate (YYYY-MM-DD): ").strip()
        country = input("Country: ").strip()

        cursor.execute("""
            INSERT INTO Users (Email, Username, Gender, Age, Birthdate, Country)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (email, username, gender, age, birthdate, country))

        conn.commit()
        print("User registered successfully.")
    except Exception as e:
        print(f"Error registering user: {e}")


def add_new_user_usage(conn):
    cursor = conn.cursor()

    try:
        email = input("User Email: ").strip()
        project_name = input("Project Name: ").strip()
        project_category = input(
            "Project Category (analytics / machine learning / field research): "
        ).strip()
        dataset_id = input("Dataset ID: ").strip()

        cursor.execute("""
            SELECT Dataset_ID
            FROM Dataset
            WHERE Dataset_ID = %s
        """, (dataset_id,))
        dataset_exists = cursor.fetchone()

        if not dataset_exists:
            print(f"Error: Dataset_ID '{dataset_id}' does not exist in Dataset table.")
            return

        cursor.execute("""
            SELECT Email
            FROM Users
            WHERE Email = %s
        """, (email,))
        user_exists = cursor.fetchone()

        if not user_exists:
            print(f"Error: User '{email}' does not exist in Users table.")
            return

        cursor.execute("""
            INSERT INTO DatasetUsage
            (Project_Name, Project_Category, Dataset_ID, User_Email)
            VALUES (%s, %s, %s, %s)
        """, (project_name, project_category, dataset_id, email))

        conn.commit()
        print("New usage added successfully.")

    except Exception as e:
        print(f"Error adding usage: {e}")

def view_usage(conn):
    cursor = conn.cursor()
    try:
        email = input("User Email: ").strip()

        cursor.execute("""
            SELECT Usage_ID, Project_Name, Project_Category, Dataset_ID, User_Email
            FROM DatasetUsage
            WHERE User_Email = %s
            ORDER BY Usage_ID
        """, (email,))

        results = cursor.fetchall()

        if not results:
            print("No usage records found.")
            return

        print("\nUsage Records:")
        for row in results:
            print(
                f"Usage_ID: {row[0]} | "
                f"Project: {row[1]} | "
                f"Category: {row[2]} | "
                f"Dataset_ID: {row[3]} | "
                f"User_Email: {row[4]}"
            )
    except Exception as e:
        print(f"Error viewing usage: {e}")


def view_datasets_by_org_type(conn):
    cursor = conn.cursor()
    try:
        organization_type = input("Organization Type (federal/state/city/etc.): ").strip()

        cursor.execute("""
            SELECT d.Dataset_ID, d.Name, o.Name
            FROM Dataset d
            JOIN Publishing_Organization o
                ON d.Organization_ID = o.Organization_ID
            WHERE o.Organization_type = %s
            ORDER BY d.Name
        """, (organization_type,))

        results = cursor.fetchall()

        if not results:
            print("No datasets found for that organization type.")
            return

        print(f"\nDatasets for organization type '{organization_type}':")
        for row in results:
            print(f"Dataset_ID: {row[0]} | Dataset: {row[1]} | Organization: {row[2]}")
    except Exception as e:
        print(f"Error viewing datasets by organization type: {e}")


def top_five_organizations(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT o.Name, COUNT(*) AS numDataset
            FROM Publishing_Organization o
            JOIN Dataset d
                ON d.Organization_ID = o.Organization_ID
            GROUP BY o.Organization_ID, o.Name
            ORDER BY numDataset DESC, o.Name ASC
            LIMIT 5
        """)

        results = cursor.fetchall()

        if not results:
            print("No organizations found.")
            return

        print("\nTop 5 contributing organizations:")
        for i, row in enumerate(results, 1):
            print(f"{i}. {row[0]} -> {row[1]} datasets")
    except Exception as e:
        print(f"Error retrieving top 5 organizations: {e}")


def datasets_by_format(conn):
    cursor = conn.cursor()
    try:
        file_format = input("Format: ").strip()

        cursor.execute("""
            SELECT DISTINCT d.Dataset_ID, d.Name
            FROM Dataset d
            JOIN File_Resource fr
                ON d.Dataset_ID = fr.Dataset_ID
            WHERE fr.Format = %s
            ORDER BY d.Name
        """, (file_format,))

        results = cursor.fetchall()

        if not results:
            print("No datasets found in that format.")
            return

        print(f"\nDatasets available in format '{file_format}':")
        for row in results:
            print(f"Dataset_ID: {row[0]} | Name: {row[1]}")
    except Exception as e:
        print(f"Error retrieving datasets by format: {e}")


def datasets_by_tag(conn):
    cursor = conn.cursor()
    try:
        tag = input("Enter tag: ").strip()

        cursor.execute("""
            SELECT DISTINCT d.Dataset_ID, d.Name
            FROM Dataset d
            JOIN Dataset_Tag dt
                ON d.Dataset_ID = dt.Dataset_ID
            JOIN Tag t
                ON dt.Tag_ID = t.Tag_ID
            WHERE t.Tag_Name = %s
            ORDER BY d.Name
        """, (tag,))

        results = cursor.fetchall()

        if not results:
            print("No datasets found for that tag.")
            return

        print(f"\nDatasets associated with tag '{tag}':")
        for row in results:
            print(f"Dataset_ID: {row[0]} | Name: {row[1]}")
    except Exception as e:
        print(f"Error retrieving datasets by tag: {e}")


def count_by_organization(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT o.Name, COUNT(*) AS total_datasets
            FROM Dataset d
            JOIN Publishing_Organization o
                ON d.Organization_ID = o.Organization_ID
            GROUP BY o.Organization_ID, o.Name
            ORDER BY total_datasets DESC, o.Name ASC
        """)

        results = cursor.fetchall()

        print("\nTotal number of datasets by organization:")
        for row in results:
            print(f"{row[0]} -> {row[1]}")
    except Exception as e:
        print(f"Error counting by organization: {e}")


def count_by_topic(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT Topic, COUNT(*) AS total_datasets
            FROM Dataset
            WHERE Topic IS NOT NULL
            GROUP BY Topic
            ORDER BY total_datasets DESC, Topic ASC
        """)

        results = cursor.fetchall()

        print("\nTotal number of datasets by topic:")
        for row in results:
            print(f"{row[0]} -> {row[1]}")
    except Exception as e:
        print(f"Error counting by topic: {e}")


def count_by_format(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT fr.Format, COUNT(DISTINCT fr.Dataset_ID) AS total_datasets
            FROM File_Resource fr
            WHERE fr.Format IS NOT NULL
            GROUP BY fr.Format
            ORDER BY total_datasets DESC, fr.Format ASC
        """)

        results = cursor.fetchall()

        print("\nTotal number of datasets by format:")
        for row in results:
            print(f"{row[0]} -> {row[1]}")
    except Exception as e:
        print(f"Error counting by format: {e}")


def count_by_org_type(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT o.Organization_type, COUNT(*) AS total_datasets
            FROM Dataset d
            JOIN Publishing_Organization o
                ON d.Organization_ID = o.Organization_ID
            WHERE o.Organization_type IS NOT NULL
            GROUP BY o.Organization_type
            ORDER BY total_datasets DESC, o.Organization_type ASC
        """)

        results = cursor.fetchall()

        print("\nTotal number of datasets by organization type:")
        for row in results:
            print(f"{row[0]} -> {row[1]}")
    except Exception as e:
        print(f"Error counting by organization type: {e}")


def top_five_datasets_by_users(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT d.Dataset_ID, d.Name, COUNT(DISTINCT du.User_Email) AS num_users
            FROM DatasetUsage du
            JOIN Dataset d
                ON du.Dataset_ID = d.Dataset_ID
            GROUP BY d.Dataset_ID, d.Name
            ORDER BY num_users DESC, d.Name ASC
            LIMIT 5
        """)

        results = cursor.fetchall()

        if not results:
            print("No dataset usage records found.")
            return

        print("\nTop 5 datasets by number of users:")
        for i, row in enumerate(results, 1):
            print(f"{i}. Dataset_ID: {row[0]} | {row[1]} -> {row[2]} users")
    except Exception as e:
        print(f"Error retrieving top 5 datasets by users: {e}")


def usage_distribution_by_project_type(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT Project_Category, COUNT(*) AS usage_count
            FROM DatasetUsage
            GROUP BY Project_Category
            ORDER BY usage_count DESC, Project_Category ASC
        """)

        results = cursor.fetchall()

        print("\nUsage distribution by project type:")
        for row in results:
            print(f"{row[0]} -> {row[1]}")
    except Exception as e:
        print(f"Error retrieving usage distribution: {e}")


def top_tags_by_project_type(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT du.Project_Category, t.Tag_Name, COUNT(*) AS tag_count
            FROM DatasetUsage du
            JOIN Dataset_Tag dt
                ON du.Dataset_ID = dt.Dataset_ID
            JOIN Tag t
                ON dt.Tag_ID = t.Tag_ID
            GROUP BY du.Project_Category, t.Tag_ID, t.Tag_Name
            ORDER BY du.Project_Category ASC, tag_count DESC, t.Tag_Name ASC
        """)

        results = cursor.fetchall()

        if not results:
            print("No tag usage data found.")
            return

        current_category = None
        shown = 0

        print("\nTop 10 tags associated with every project type:")
        for category, tag_name, count in results:
            if category != current_category:
                current_category = category
                shown = 0
                print(f"\nProject Category: {category}")

            if shown < 10:
                print(f"  {shown + 1}. {tag_name} -> {count}")
                shown += 1
    except Exception as e:
        print(f"Error retrieving top tags by project type: {e}")
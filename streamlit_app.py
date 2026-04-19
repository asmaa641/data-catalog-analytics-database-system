import streamlit as st
import pandas as pd
from db import get_connection

st.set_page_config(
    page_title="Data.gov Analytics System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }
        .metric-card {
            padding: 1rem;
            border-radius: 16px;
            background-color: #f7f7f9;
            border: 1px solid #e6e6e6;
        }
        .section-title {
            margin-top: 0.5rem;
            margin-bottom: 0.3rem;
        }
        .small-note {
            color: #6b7280;
            font-size: 0.92rem;
        }
    </style>
""", unsafe_allow_html=True)


def run_select_query(query, params=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(rows, columns=columns)
    finally:
        conn.close()

def run_action_query(query, params=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
    finally:
        conn.close()

@st.cache_data(show_spinner=False)
def get_dashboard_metrics():
    metrics = {}

    metrics["datasets"] = run_select_query("SELECT COUNT(*) AS total FROM Dataset").iloc[0]["total"]
    metrics["organizations"] = run_select_query("SELECT COUNT(*) AS total FROM Publishing_Organization").iloc[0]["total"]
    metrics["tags"] = run_select_query("SELECT COUNT(*) AS total FROM Tag").iloc[0]["total"]
    metrics["usage"] = run_select_query("SELECT COUNT(*) AS total FROM DatasetUsage").iloc[0]["total"]

    return metrics

def show_df(df, file_name="results.csv"):
    if df.empty:
        st.warning("No results found.")
    else:
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "Download results as CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name=file_name,
            mime="text/csv"
        )

st.sidebar.title("Navigation")

section = st.sidebar.radio(
    "Go to",
    ["Dashboard", "User Operations", "Dataset Exploration", "Analytics"]
)

st.title("📊 Data.gov Application Layer")
st.caption("Hosted MySQL database + Streamlit interface for Milestone 3")


if section == "Dashboard":
    st.subheader("System Overview")

    metrics = get_dashboard_metrics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Datasets", f"{metrics['datasets']:,}")
    c2.metric("Organizations", f"{metrics['organizations']:,}")
    c3.metric("Tags", f"{metrics['tags']:,}")
    c4.metric("Usage Records", f"{metrics['usage']:,}")

    st.markdown("---")

    left, right = st.columns([1.3, 1])

    with left:
        st.markdown("### Top 5 Contributing Organizations")
        try:
            df = run_select_query("""
                SELECT o.Name AS Organization_Name, COUNT(*) AS Number_of_Datasets
                FROM Publishing_Organization o
                JOIN Dataset d
                    ON d.Organization_ID = o.Organization_ID
                GROUP BY o.Organization_ID, o.Name
                ORDER BY Number_of_Datasets DESC, o.Name ASC
                LIMIT 5
            """)
            show_df(df, "top_organizations.csv")
        except Exception as e:
            st.error(f"Error: {e}")

    with right:
        st.markdown("### Usage Distribution by Project Type")
        try:
            df = run_select_query("""
                SELECT Project_Category, COUNT(*) AS Usage_Count
                FROM DatasetUsage
                GROUP BY Project_Category
                ORDER BY Usage_Count DESC, Project_Category ASC
            """)
            if df.empty:
                st.warning("No usage data found.")
            else:
                st.bar_chart(df.set_index("Project_Category"))
                show_df(df, "usage_distribution.csv")
        except Exception as e:
            st.error(f"Error: {e}")


elif section == "User Operations":
    action = st.selectbox(
        "Choose Action",
        ["Register User", "Add Usage", "View Usage"]
    )

    if action == "Register User":
        st.subheader("Register a New User")
        st.markdown('<div class="small-note">Create a new user record in the hosted database.</div>', unsafe_allow_html=True)

        with st.form("register_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("Email")
                username = st.text_input("Username")
                gender = st.text_input("Gender")
            with col2:
                age = st.number_input("Age", min_value=1, max_value=120, step=1)
                birthdate = st.text_input("Birthdate (YYYY-MM-DD)")
                country = st.text_input("Country")

            submitted = st.form_submit_button("Register User")

            if submitted:
                try:
                    run_action_query("""
                        INSERT INTO Users (Email, Username, Gender, Age, Birthdate, Country)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (email, username, gender, age, birthdate, country))
                    st.success("User registered successfully.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error: {e}")

    elif action == "Add Usage":
        st.subheader("Add Dataset Usage")
        st.markdown('<div class="small-note">Record that a user used a dataset in a specific project.</div>', unsafe_allow_html=True)

        with st.form("add_usage_form"):
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("User Email")
                project_name = st.text_input("Project Name")
            with col2:
                project_category = st.text_input("Project Category")
                dataset_id = st.number_input("Dataset ID", min_value=1, step=1)

            submitted = st.form_submit_button("Add Usage")

            if submitted:
                try:
                    run_action_query("""
                        INSERT INTO DatasetUsage (Project_Name, Project_Category, Dataset_ID, User_Email)
                        VALUES (%s, %s, %s, %s)
                    """, (project_name, project_category, dataset_id, email))
                    st.success("New usage added successfully.")
                except Exception as e:
                    st.error(f"Error: {e}")

    elif action == "View Usage":
        st.subheader("View Usage for a User")

        email = st.text_input("Enter User Email")
        search = st.button("View Usage")

        if search:
            try:
                df = run_select_query("""
                    SELECT Usage_ID, Project_Name, Project_Category, Dataset_ID, User_Email
                    FROM DatasetUsage
                    WHERE User_Email = %s
                    ORDER BY Usage_ID
                """, (email,))
                show_df(df, "user_usage.csv")
            except Exception as e:
                st.error(f"Error: {e}")


elif section == "Dataset Exploration":
    action = st.selectbox(
        "Choose Exploration Type",
        ["Datasets by Organization Type", "Datasets by Format", "Datasets by Tag"]
    )

    if action == "Datasets by Organization Type":
        st.subheader("Explore Datasets by Organization Type")

        organization_type = st.text_input("Organization Type")
        if st.button("Show Datasets by Organization Type"):
            try:
                df = run_select_query("""
                    SELECT d.Dataset_ID, d.Name AS Dataset_Name, o.Name AS Organization_Name, o.Organization_type
                    FROM Dataset d
                    JOIN Publishing_Organization o
                        ON d.Organization_ID = o.Organization_ID
                    WHERE o.Organization_type = %s
                    ORDER BY d.Name
                """, (organization_type,))
                show_df(df, "datasets_by_org_type.csv")
            except Exception as e:
                st.error(f"Error: {e}")

    elif action == "Datasets by Format":
        st.subheader("Explore Datasets by Format")

        file_format = st.text_input("Format (e.g. CSV, JSON, XML)")
        if st.button("Show Datasets by Format"):
            try:
                df = run_select_query("""
                    SELECT DISTINCT d.Dataset_ID, d.Name AS Dataset_Name, fr.Format
                    FROM Dataset d
                    JOIN File_Resource fr
                        ON d.Dataset_ID = fr.Dataset_ID
                    WHERE fr.Format = %s
                    ORDER BY d.Name
                """, (file_format,))
                show_df(df, "datasets_by_format.csv")
            except Exception as e:
                st.error(f"Error: {e}")

    elif action == "Datasets by Tag":
        st.subheader("Explore Datasets by Tag")

        tag = st.text_input("Tag")
        if st.button("Show Datasets by Tag"):
            try:
                df = run_select_query("""
                    SELECT DISTINCT d.Dataset_ID, d.Name AS Dataset_Name, t.Tag_Name
                    FROM Dataset d
                    JOIN Dataset_Tag dt
                        ON d.Dataset_ID = dt.Dataset_ID
                    JOIN Tag t
                        ON dt.Tag_ID = t.Tag_ID
                    WHERE t.Tag_Name = %s
                    ORDER BY d.Name
                """, (tag,))
                show_df(df, "datasets_by_tag.csv")
            except Exception as e:
                st.error(f"Error: {e}")

elif section == "Analytics":
    action = st.selectbox(
        "Choose Analytics View",
        [
            "Top 5 Organizations",
            "Count by Organization",
            "Count by Topic",
            "Count by Format",
            "Count by Organization Type",
            "Top 5 Datasets by Users",
            "Usage Distribution by Project Type",
            "Top 10 Tags by Project Type"
        ]
    )

    if action == "Top 5 Organizations":
        st.subheader("Top 5 Contributing Organizations")
        if st.button("Run Query"):
            try:
                df = run_select_query("""
                    SELECT o.Name AS Organization_Name, COUNT(*) AS Number_of_Datasets
                    FROM Publishing_Organization o
                    JOIN Dataset d
                        ON d.Organization_ID = o.Organization_ID
                    GROUP BY o.Organization_ID, o.Name
                    ORDER BY Number_of_Datasets DESC, o.Name ASC
                    LIMIT 5
                """)
                show_df(df, "top_5_organizations.csv")
            except Exception as e:
                st.error(f"Error: {e}")

    elif action == "Count by Organization":
        st.subheader("Total Number of Datasets by Organization")
        if st.button("Run Query"):
            try:
                df = run_select_query("""
                    SELECT o.Name AS Organization_Name, COUNT(*) AS Total_Datasets
                    FROM Dataset d
                    JOIN Publishing_Organization o
                        ON d.Organization_ID = o.Organization_ID
                    GROUP BY o.Organization_ID, o.Name
                    ORDER BY Total_Datasets DESC, o.Name ASC
                """)
                show_df(df, "count_by_organization.csv")
            except Exception as e:
                st.error(f"Error: {e}")

    elif action == "Count by Topic":
        st.subheader("Total Number of Datasets by Topic")
        if st.button("Run Query"):
            try:
                df = run_select_query("""
                    SELECT Topic, COUNT(*) AS Total_Datasets
                    FROM Dataset
                    WHERE Topic IS NOT NULL
                    GROUP BY Topic
                    ORDER BY Total_Datasets DESC, Topic ASC
                """)
                show_df(df, "count_by_topic.csv")
            except Exception as e:
                st.error(f"Error: {e}")

    elif action == "Count by Format":
        st.subheader("Total Number of Datasets by Format")
        if st.button("Run Query"):
            try:
                df = run_select_query("""
                    SELECT fr.Format, COUNT(DISTINCT fr.Dataset_ID) AS Total_Datasets
                    FROM File_Resource fr
                    WHERE fr.Format IS NOT NULL
                    GROUP BY fr.Format
                    ORDER BY Total_Datasets DESC, fr.Format ASC
                """)
                show_df(df, "count_by_format.csv")
            except Exception as e:
                st.error(f"Error: {e}")

    elif action == "Count by Organization Type":
        st.subheader("Total Number of Datasets by Organization Type")
        if st.button("Run Query"):
            try:
                df = run_select_query("""
                    SELECT o.Organization_type, COUNT(*) AS Total_Datasets
                    FROM Dataset d
                    JOIN Publishing_Organization o
                        ON d.Organization_ID = o.Organization_ID
                    WHERE o.Organization_type IS NOT NULL
                    GROUP BY o.Organization_type
                    ORDER BY Total_Datasets DESC, o.Organization_type ASC
                """)
                show_df(df, "count_by_org_type.csv")
            except Exception as e:
                st.error(f"Error: {e}")

    elif action == "Top 5 Datasets by Users":
        st.subheader("Top 5 Datasets by Number of Users")
        if st.button("Run Query"):
            try:
                df = run_select_query("""
                    SELECT d.Dataset_ID, d.Name AS Dataset_Name, COUNT(DISTINCT du.User_Email) AS Number_of_Users
                    FROM DatasetUsage du
                    JOIN Dataset d
                        ON du.Dataset_ID = d.Dataset_ID
                    GROUP BY d.Dataset_ID, d.Name
                    ORDER BY Number_of_Users DESC, d.Name ASC
                    LIMIT 5
                """)
                show_df(df, "top_5_datasets_by_users.csv")
            except Exception as e:
                st.error(f"Error: {e}")

    elif action == "Usage Distribution by Project Type":
        st.subheader("Usage Distribution by Project Type")
        if st.button("Run Query"):
            try:
                df = run_select_query("""
                    SELECT Project_Category, COUNT(*) AS Usage_Count
                    FROM DatasetUsage
                    GROUP BY Project_Category
                    ORDER BY Usage_Count DESC, Project_Category ASC
                """)
                if df.empty:
                    st.warning("No data found.")
                else:
                    col1, col2 = st.columns([1.1, 1])
                    with col1:
                        st.dataframe(df, use_container_width=True)
                    with col2:
                        st.bar_chart(df.set_index("Project_Category"))
                    st.download_button(
                        "Download results as CSV",
                        df.to_csv(index=False).encode("utf-8"),
                        "usage_distribution.csv",
                        "text/csv"
                    )
            except Exception as e:
                st.error(f"Error: {e}")

    elif action == "Top 10 Tags by Project Type":
        st.subheader("Top 10 Tags Associated with Every Project Type")
        if st.button("Run Query"):
            try:
                df = run_select_query("""
                    SELECT du.Project_Category, t.Tag_Name, COUNT(*) AS Tag_Count
                    FROM DatasetUsage du
                    JOIN Dataset_Tag dt
                        ON du.Dataset_ID = dt.Dataset_ID
                    JOIN Tag t
                        ON dt.Tag_ID = t.Tag_ID
                    GROUP BY du.Project_Category, t.Tag_ID, t.Tag_Name
                    ORDER BY du.Project_Category ASC, Tag_Count DESC, t.Tag_Name ASC
                """)
                if df.empty:
                    st.warning("No data found.")
                else:
                    for category in df["Project_Category"].unique():
                        st.markdown(f"### {category}")
                        category_df = df[df["Project_Category"] == category].head(10)
                        st.dataframe(category_df, use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")
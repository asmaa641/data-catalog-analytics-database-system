from db import get_connection
from queries import (
    register_user,
    add_new_user_usage,
    view_usage,
    view_datasets_by_org_type,
    top_five_organizations,
    datasets_by_format,
    datasets_by_tag,
    count_by_organization,
    count_by_topic,
    count_by_format,
    count_by_org_type,
    top_five_datasets_by_users,
    usage_distribution_by_project_type,
    top_tags_by_project_type
)

def print_menu():
    print("\n===== Data.gov Application Layer =====")
    print("1. Register a user")
    print("2. Add a new user usage for a dataset")
    print("3. View existing usage information for a user")
    print("4. View datasets by organization type")
    print("5. View top 5 contributing organizations")
    print("6. View datasets available in a given format")
    print("7. View datasets associated with a given tag")
    print("8. Show total number of datasets by organization")
    print("9. Show total number of datasets by topic")
    print("10. Show total number of datasets by format")
    print("11. Show total number of datasets by organization type")
    print("12. Show top 5 datasets by number of users")
    print("13. Show dataset usage distribution by project type")
    print("14. Display top 10 tags associated with every project type")
    print("0. Exit")


def main():
    conn = None
    try:
        conn = get_connection()
        print("Connected to remote database successfully.")

        while True:
            print_menu()
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                register_user(conn)
            elif choice == "2":
                add_new_user_usage(conn)
            elif choice == "3":
                view_usage(conn)
            elif choice == "4":
                view_datasets_by_org_type(conn)
            elif choice == "5":
                top_five_organizations(conn)
            elif choice == "6":
                datasets_by_format(conn)
            elif choice == "7":
                datasets_by_tag(conn)
            elif choice == "8":
                count_by_organization(conn)
            elif choice == "9":
                count_by_topic(conn)
            elif choice == "10":
                count_by_format(conn)
            elif choice == "11":
                count_by_org_type(conn)
            elif choice == "12":
                top_five_datasets_by_users(conn)
            elif choice == "13":
                usage_distribution_by_project_type(conn)
            elif choice == "14":
                top_tags_by_project_type(conn)
            elif choice == "0":
                print("Exiting application.")
                break
            else:
                print("Invalid choice. Please try again.")

    except Exception as e:
        print(f"Application error: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()
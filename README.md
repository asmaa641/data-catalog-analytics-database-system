# Data Catalog Analytics Database System
### Project Overview

This project is a complete Data Catalog Analytics Database System built using MySQL and Python. It is based on real public datasets collected from Data.gov using the CKAN API and includes database design, data collection, database population, and a full application layer connected to a remotely hosted MySQL server.

The project was developed across multiple milestones:

1. Database Design and Schema Creation
2. Data Collection and Database Population
3. Application Layer Implementation

The system allows users to explore datasets, publishing organizations, tags, resources, and user usage analytics through both a Command-Line Interface (CLI) and a Streamlit-based GUI.

## Milestone I — Database Design
### Objective

Design a relational database system for storing and managing Data.gov datasets and related metadata.

### Main Tables
#### Core Tables
- Dataset
- Publishing_Organization
- Tag
- File_Resource
- Users
- DatasetUsage
#### Relationship Tables
- Dataset_Tag
#### Key Design Concepts
- Primary Keys
- Foreign Keys
- Normalization
- Relational Modeling
- Data Integrity Constraint
#### Example Relationships
- One organization can publish many datasets
- One dataset can have many tags
- One user can use many datasets
- One dataset can be used by many users

## Milestone II — Data Collection and Population
### Objective

Collect real dataset metadata from Data.gov using the CKAN API and populate the MySQL database.

### Tools Used
- Python
- Requests
- MySQL
- CKAN API
- MySQL Workbench
- Aiven (Remote MySQL Hosting)
### Data Source

Data.gov API using CKAN package_search endpoint.

### Data Collected
- Dataset information
- Publishing organizations
- Tags
- File resources
- Dataset metadata
### Result

Thousands of real datasets were inserted successfully into the database and exported as SQL dump files.

## Milestone III — Application Layer
### Objective

Build an application that connects to the hosted remote MySQL database and performs required transactions and analytical queries.

The database must be hosted remotely and must not rely on localhost.

## Implemented Interfaces
1. Command-Line Interface (CLI)
app.py
2. Web-Based GUI (Bonus)
streamlit_app.py using Streamlit
## Features Implemented
### User Operations
- Register a new user
- Add a new dataset usage record
- View usage information for a user
### Dataset Filtering
- View datasets by organization type
- View datasets available in a given format
- View datasets associated with a given tag
### Analytics
- Top 5 contributing organizations
- Total datasets by organization
- Total datasets by topic
- Total datasets by format
- Total datasets by organization type
- Top 5 datasets by number of users
- Usage distribution by project type
- Top 10 tags associated with every project type
### Additional Project Components
#### Postman Collection
- A Postman folder is included for API testing and validation
- Used to test CKAN API requests before integrating the crawler with MySQL
- Helped verify request parameters, API responses, and dataset retrieval structure
- Supports milestone verification by documenting tested endpoints and request flows
## Technologies Used
### Backend
- Python
- MySQL
- PyMySQL
- Python Dotenv
### GUI
- Streamlit
- Pandas
### Hosting
- Aiven MySQL Cloud Hosting
### Data Collection
- CKAN API
- Requests Library

### Setup Instructions
1. Install Dependencies
```
pip install -r requirements.txt
```

Or manually:
```
pip install pymysql python-dotenv cryptography streamlit pandas
Environment Variables
```
Create a .env file in the project root:

AVN_HOST=your_aiven_host
AVN_USER=avnadmin
AVN_PASSWORD=your_password
AVN_DB=defaultdb
AVN_PORT=23831

### Running the CLI Application
```
python app.py
```

This opens the menu-driven application for all required milestone operations.

### Running the GUI Application
```
streamlit run streamlit_app.py
```

This launches the web-based Streamlit interface for bonus GUI marks.

### Database Dump

The latest remote hosted database dump is included as:

latest_dump.sql

It includes:

- Table structures
- Inserted records
- Latest user usage entries
- Current hosted database state

### Notes
- The system uses a real hosted MySQL database through Aiven.
- No localhost database is used for final milestone evaluation.
- Streamlit GUI was added for bonus GUI/Web-based application marks.
- Error handling was added to improve demo stability.
- The latest SQL dump reflects the final production-ready version of the project.

import mysql.connector
import requests

# Fetch data from the API
url = "https://api.sportradar.com/tennis/trial/v3/en/competitions.json?api_key=Peab8MyrHuoAenp8rM7RpOaEv7eLImIuaj6HB7Cj"
headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)
data = response.json()

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Sai@12345",
    database="Sport"
)

cursor = conn.cursor()

# Create the Categories table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Categories (
        Category_ID VARCHAR(250) PRIMARY KEY,
        Category_Name VARCHAR(250) NOT NULL
    )
''')

# Create the Competitions table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Competitions (
        Competition_ID VARCHAR(250) PRIMARY KEY,
        Competition_Name VARCHAR(250) NOT NULL,
        Parent_ID VARCHAR(250),
        Type VARCHAR(100),
        Gender VARCHAR(50),
        Category_ID VARCHAR(250),
        FOREIGN KEY (Category_ID) REFERENCES Categories(Category_ID)
    )
''')

# Insert data into the tables
for competition in data["competitions"]:
    # Extract data for the Categories table
    category_id = competition["category"]["id"]
    category_name = competition["category"]["name"]

    # Insert into Categories table (avoid duplicates using INSERT IGNORE)
    cursor.execute('''
        INSERT IGNORE INTO Categories (Category_ID, Category_Name)
        VALUES (%s, %s)
    ''', (category_id, category_name))

    # Extract data for the Competitions table
    competition_id = competition["id"]
    competition_name = competition["name"]
    parent_id = competition.get("parent_id", None)
    competition_type = competition["type"]
    gender = competition.get("gender", None)

    # Insert into Competitions table (avoid duplicates using ON DUPLICATE KEY UPDATE)
    cursor.execute('''
        INSERT INTO Competitions (Competition_ID, Competition_Name, Parent_ID, Type, Gender, Category_ID)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            Competition_Name = VALUES(Competition_Name),
            Parent_ID = VALUES(Parent_ID),
            Type = VALUES(Type),
            Gender = VALUES(Gender),
            Category_ID = VALUES(Category_ID)
    ''', (competition_id, competition_name, parent_id, competition_type, gender, category_id))

# Commit changes and close connection
conn.commit()
cursor.close()
conn.close()

print("Data inserted successfully into Categories and Competitions tables!")

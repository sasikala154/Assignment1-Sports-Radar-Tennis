import mysql.connector
import requests

# Fetch data from the API
url = "https://api.sportradar.com/tennis/trial/v3/en/complexes.json?api_key=Peab8MyrHuoAenp8rM7RpOaEv7eLImIuaj6HB7Cj"
headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
else:
    print(f"API request failed with status code {response.status_code}")
    exit()

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Sai@12345",
    database="Sport"
)
cursor = conn.cursor()

# Create the Complexes table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Complexes (
        Complex_ID CHAR(50) PRIMARY KEY,
        Complex_Name VARCHAR(100) NOT NULL
    )
''')

# Create the Venues table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Venues (
        Venue_ID CHAR(50) PRIMARY KEY,
        Venue_Name VARCHAR(100) NOT NULL,
        City_Name VARCHAR(100) NOT NULL,
        Country_Name VARCHAR(100) NOT NULL,
        Country_Code CHAR(3) NOT NULL,
        Timezone VARCHAR(100) NOT NULL,
        Complex_ID CHAR(50),
        FOREIGN KEY (Complex_ID) REFERENCES Complexes(Complex_ID)
    )
''')

# Insert data into the tables
for complex_item in data.get("complexes", []):
    Complex_ID = complex_item["id"]
    Complex_Name = complex_item["name"]

    # Insert into the Complexes table
    cursor.execute('''
        INSERT IGNORE INTO Complexes (Complex_ID, Complex_Name)
        VALUES (%s, %s)
    ''', (Complex_ID, Complex_Name))

    # Insert venues related to the complex
    for venue in complex_item.get("venues", []):
        Venue_ID = venue["id"]
        Venue_Name = venue["name"]
        City_Name = venue.get("city_name", "N/A")
        Country_Name = venue.get("country_name", "N/A")
        Country_Code = venue.get("country_code", "N/A")
        Timezone = venue.get("timezone", "N/A")

        # Insert into the Venues table
        cursor.execute('''
            INSERT IGNORE INTO Venues (Venue_ID, Venue_Name, City_Name, Country_Name, Country_Code, Timezone, Complex_ID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (Venue_ID, Venue_Name, City_Name, Country_Name, Country_Code, Timezone, Complex_ID))

# Commit changes and close connection
conn.commit()
cursor.close()
conn.close()

print("Data inserted successfully into Complexes and Venues tables!")

import mysql.connector
import requests

# Fetch data from the API
url = "https://api.sportradar.com/tennis/trial/v3/en/double_competitors_rankings.json?api_key=Peab8MyrHuoAenp8rM7RpOaEv7eLImIuaj6HB7Cj"
headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)  
data = response.json()

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",           # Replace with your MySQL server hostname
    user="root",                # Replace with your MySQL username
    password="Sai@12345",  # Replace with your MySQL password
    database="Sport"           # Replace with your database name
)

cursor = conn.cursor()

# Drop tables if they already exist to avoid schema conflicts
cursor.execute('''
    DROP TABLE IF EXISTS Competitor_Rankings, Competitors
''')

# Create the Competitors table
cursor.execute('''
    CREATE TABLE Competitors (
        Competitor_ID VARCHAR(50) PRIMARY KEY,
        Name VARCHAR(100) NOT NULL,
        Country VARCHAR(100) NOT NULL,
        Country_Code CHAR(3) NOT NULL,
        Abbreviation VARCHAR(10) NOT NULL
    )
''')

# Create the Competitor_Rankings table
cursor.execute('''
    CREATE TABLE Competitor_Rankings (
        Rank_ID INT PRIMARY KEY AUTO_INCREMENT,
        `Rank` INT NOT NULL,
        Movement INT NOT NULL,
        Points INT NOT NULL,
        Competitions_Played INT NOT NULL,
        Competitor_ID VARCHAR(50),
        Week INT,
        FOREIGN KEY (Competitor_ID) REFERENCES Competitors(Competitor_ID)
    )
''')

# Insert data into the Competitors table
for ranking in data["rankings"]:
    for competitor_ranking in ranking.get("competitor_rankings", []):
        competitor = competitor_ranking.get("competitor", {})
        competitor_id = competitor.get("id", "N/A")
        name = competitor.get("name", "N/A")
        country = competitor.get("country", "N/A")
        country_code = competitor.get("country_code", "N/A")
        abbreviation = competitor.get("abbreviation", "N/A")

        # Insert into the Competitors table
        cursor.execute('''
            INSERT INTO Competitors (Competitor_ID, Name, Country, Country_Code, Abbreviation)
            VALUES (%s, %s, %s, %s, %s)
        ''', (competitor_id, name, country, country_code, abbreviation))

# Insert data into the Competitor_Rankings table
for ranking in data["rankings"]:
    for competitor_ranking in ranking.get("competitor_rankings", []):
        rank = competitor_ranking.get("rank", None)
        movement = competitor_ranking.get("movement", "N/A")
        points = competitor_ranking.get("points", 0)
        competitions_played = competitor_ranking.get("competitions_played", 0)
        competitor_id = competitor_ranking.get("competitor", {}).get("id", "N/A")
        week = ranking.get("week", None)

        # Insert into the Competitor_Rankings table
        cursor.execute('''
            INSERT INTO Competitor_Rankings (`Rank`, Movement, Points, Competitions_Played, Competitor_ID, Week)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (rank, movement, points, competitions_played, competitor_id, week))

# Commit changes and close connection
conn.commit()
cursor.close()
conn.close()

print("Data inserted into Competitors and Competitor_Rankings tables successfully!")

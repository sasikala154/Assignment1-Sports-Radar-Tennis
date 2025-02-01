import streamlit as st
import mysql.connector
import pandas as pd
import altair as alt

# Set up the MySQL connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sai@12345",
        database="Sport"
    )

# Function to fetch data from the database
def fetch_data(query):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return pd.DataFrame(result)

# Streamlit app
st.set_page_config(page_title="Tennis Data Analytics", layout="wide")
st.title("Game Analytics: Unlocking Tennis Data with SportRadar API")
st.sidebar.title("Navigation")
options = ["Homepage", "Search Competitors", "Country-Wise Analysis", "Leaderboards", "Competitions", "Venues"]
page = st.sidebar.radio("Go to", options)

if page == "Homepage":
    st.header("Homepage Dashboard")

    total_competitors = fetch_data("SELECT COUNT(*) AS total FROM Competitors").iloc[0]['total']
    total_countries = fetch_data("SELECT COUNT(DISTINCT country) AS total FROM Competitors").iloc[0]['total']
    highest_points = fetch_data("SELECT MAX(points) AS max_points FROM Competitor_Rankings").iloc[0]['max_points']
    total_competitions = fetch_data("SELECT COUNT(*) AS total FROM Competitions").iloc[0]['total']

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Competitors", total_competitors)
    col2.metric("Countries Represented", total_countries)
    col3.metric("Highest Points", highest_points)
    col4.metric("Total Competitions", total_competitions)

elif page == "Search Competitors":
    st.header("Search and Filter Competitors")

    name = st.text_input("Search by Name")
    country = st.text_input("Filter by Country")
    min_rank, max_rank = st.slider("Rank Range", 1, 500, (1, 100))
    
    query = """
    SELECT c.name, c.country, cr.rank, cr.points, cr.competitions_played
    FROM Competitors c
    JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
    WHERE cr.rank BETWEEN %s AND %s
    """
    params = [min_rank, max_rank]

    if name:
        query += " AND c.name LIKE %s"
        params.append(f"%{name}%")

    if country:
        query += " AND c.country = %s"
        params.append(country)

    competitors = fetch_data(query % tuple(params))
    st.dataframe(competitors)

elif page == "Country-Wise Analysis":
    st.header("Country-Wise Analysis")
    country_data = fetch_data("""
        SELECT country, COUNT(*) AS num_competitors, AVG(points) AS avg_points
        FROM Competitors c
        JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
        GROUP BY country
    """)
    st.dataframe(country_data)
    chart = alt.Chart(country_data).mark_bar().encode(x="country", y="avg_points", tooltip=["avg_points"])
    st.altair_chart(chart, use_container_width=True)

elif page == "Leaderboards":
    st.header("Leaderboards")
    top_competitors = fetch_data("""
        SELECT c.name, c.country, cr.rank, cr.points
        FROM Competitors c
        JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
        ORDER BY cr.rank ASC
        LIMIT 10
    """)
    st.subheader("Top 10 Competitors")
    st.dataframe(top_competitors)

elif page == "Competitions":
    st.header("Competition Analysis")
    competitions = fetch_data("""
        SELECT c.Competition_name, cat.Category_name, c.Type
        FROM Competitions c
        JOIN Categories cat ON c.Category_id = cat.Category_id
    """)
    st.dataframe(competitions)
    chart = alt.Chart(competitions).mark_bar().encode(
        x="Category_name", y="count()", tooltip=["count()"]
    ).properties(title="Competitions per Category")
    st.altair_chart(chart, use_container_width=True)

elif page == "Venues":
    st.header("Venues Information")
    venues = fetch_data("""
        SELECT v.Venue_name, v.City_name, v.Country_name, v.Timezone, c.Complex_name
        FROM Venues v
        JOIN Complexes c ON v.Complex_id = c.Complex_id
    """)
    st.dataframe(venues)
    st.subheader("Venues per Country")
    country_venues = fetch_data("""
        SELECT Country_name, COUNT(*) AS Venue_Count
        FROM Venues
        GROUP BY Country_name
    """)
    st.dataframe(country_venues)
    chart = alt.Chart(country_venues).mark_bar().encode(
        x="Country_name", y="Venue_Count", tooltip=["Venue_Count"]
    ).properties(title="Venues Count by Country")
    st.altair_chart(chart, use_container_width=True)

st.sidebar.info("Developed as part of 'Game Analytics: Unlocking Tennis Data with SportRadar API' project.")

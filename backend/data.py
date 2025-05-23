from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import folium
import os

DATABASE_URL = "sqlite:///flights.sqlite3"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FlightData:
    """
    A class that handles database queries related to flight data.

    Attributes:
        db_session: A database session object for executing queries.

    Methods:
        _execute_query(query: str, params: dict): Executes a query and returns the result as a list of dictionaries.
        get_flight_by_id(flight_id: int): Returns flight details by ID.
        get_flights_by_date(day: int, month: int, year: int): Returns flights for a specific date.
        get_delayed_flights_by_airline(airline: str): Returns delayed flights for a specific airline.
        get_delayed_flights_by_airport(airport: str): Returns delayed flights for a specific airport.
        get_delayed_flights_by_hour(threshold: int): Returns delayed flights grouped by hour, with an optional threshold for delay.
    """

    def __init__(self, db_session):
        """
        Initializes the FlightData object with a database session.
        """
        self.db_session = db_session

    def _execute_query(self, query: str, params: dict):
        """
        Executes a query on the database and returns the result as a list of dictionaries.

        Args:
            query: SQL query string.
            params: Parameters to be passed with the query.

        Returns:
            A list of dictionaries with query results.
        """
        try:
            result = self.db_session.execute(text(query), params)
            columns = result.keys()
            result_dicts = [dict(zip(columns, row)) for row in result.fetchall()]
            print(f"Columns: {columns}")
            print(f"First 5 Results: {result_dicts[:5]}")  # Log the first few rows for debugging
            return result_dicts
        except Exception as e:
            print(f"Database error: {str(e)}")
            return []

    def get_flight_by_id(self, flight_id: int):
        """
        Fetches flight details by flight ID.

        Args:
            flight_id: The ID of the flight.

        Returns:
            A list of dictionaries containing flight data.
        """
        params = {'id': flight_id}
        query = """
        SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY
        FROM flights
        JOIN airlines ON flights.airline = airlines.id
        WHERE flights.ID = :id
        """
        return self._execute_query(query, params)

    def get_flights_by_date(self, day: int, month: int, year: int):
        """
        Fetches flights for a specific date.

        Args:
            day: Day of the month.
            month: Month of the year.
            year: Year.

        Returns:
            A list of dictionaries containing flight data.
        """
        query = """
        SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY
        FROM flights
        JOIN airlines ON flights.airline = airlines.id
        WHERE flights.DAY = :day AND flights.MONTH = :month AND flights.YEAR = :year
        Limit 10
        """
        params = {'day': day, 'month': month, 'year': year}
        return self._execute_query(query, params)

    def get_delayed_flights_by_airline(self, airline: str):
        """
        Fetches delayed flights for a specific airline.

        Args:
            airline: The name of the airline.

        Returns:
            A list of dictionaries containing delayed flight data.
        """
        params = {'airline': f"%{airline}%"}
        query = """
        SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY
        FROM flights
        JOIN airlines ON flights.airline = airlines.id
        WHERE airlines.airline LIKE :airline
        AND flights.DEPARTURE_DELAY > 20
        ORDER BY DEPARTURE_DELAY DESC
        Limit 10
        """
        return self._execute_query(query, params)

    def get_delayed_flights_by_airport(self, airport: str):
        """
        Fetches delayed flights for a specific airport.

        Args:
            airport: The airport code (e.g., "JFK").

        Returns:
            A list of dictionaries containing delayed flight data.
        """
        params = {'airport': f"%{airport}%"}
        query = """
        SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY
        FROM flights
        JOIN airlines ON flights.airline = airlines.id
        WHERE flights.ORIGIN_AIRPORT LIKE :airport
        AND flights.DEPARTURE_DELAY > 20
        Limit 10
        """
        return self._execute_query(query, params)

    def get_delayed_flights_by_hour(self, threshold: int):
        """
        Fetches delayed flights grouped by hour.

        Args:
            threshold: Minimum departure delay to consider as "delayed."

        Returns:
            A list of dictionaries containing delayed flight data, grouped by hour.
        """
        query = """
        SELECT 
            CAST(substr(flights.scheduled_departure, 1, 2) AS INTEGER) AS hour,
            COUNT(flights.id) AS total_flights,
            SUM(CASE WHEN flights.departure_delay > 20 THEN 1 ELSE 0 END) AS delayed_flights,
            ROUND(AVG(flights.departure_delay), 2) AS average_departure_delay
        FROM flights
        WHERE flights.departure_delay >= :threshold
        GROUP BY hour
        ORDER BY hour
        Limit 10
        """
        return self._execute_query(query, {"threshold": threshold})


# Function to plot the delays by airline and save as a PNG image
def plot_delays_by_airline(file_path: str):
    """
    Generates a bar plot for the percentage of delayed flights per airline and saves it as a PNG image.

    Args:
        file_path: The path where the image will be saved.
    """
    query = """
    SELECT 
        airlines.airline AS AIRLINE, 
        COUNT(flights.id) AS total_flights,
        SUM(CASE WHEN flights.departure_delay > 20 THEN 1 ELSE 0 END) AS delayed_flights
    FROM flights
    JOIN airlines ON flights.airline = airlines.id
    GROUP BY airlines.airline
    """
    df = pd.read_sql(query, engine)
    df['percent_delayed'] = (df['delayed_flights'] / df['total_flights']) * 100

    plt.figure(figsize=(12,6))
    sns.barplot(x='AIRLINE', y='percent_delayed', data=df)
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Percentage of Delayed Flights')
    plt.title('Percentage of Delayed Flights by Airline')
    plt.tight_layout()

    # Save the figure to a PNG image
    plt.savefig(file_path, format="png")
    plt.close()


# Function to plot the delays by hour and save as a PNG image
def plot_delays_by_hour(file_path: str):
    """
    Generates a bar plot for the percentage of delayed flights by hour and saves it as a PNG image.

    Args:
        file_path: The path where the image will be saved.
    """
    query = """
    SELECT 
        CAST(substr(flights.scheduled_departure, 1, 2) AS INTEGER) AS hour,
        COUNT(flights.id) AS total_flights,
        SUM(CASE WHEN flights.departure_delay > 20 THEN 1 ELSE 0 END) AS delayed_flights
    FROM flights
    GROUP BY hour
    ORDER BY hour
    """
    df = pd.read_sql(query, engine)
    df['percent_delayed'] = (df['delayed_flights'] / df['total_flights']) * 100

    plt.figure(figsize=(12,6))
    sns.barplot(x='hour', y='percent_delayed', data=df, palette="YlGnBu")
    plt.ylabel('Percentage of Delayed Flights')
    plt.xlabel('Hour of Day')
    plt.title('Percentage of Delayed Flights by Hour of Day')
    plt.xticks(range(24))  # Hours from 0 to 23
    plt.tight_layout()

    # Save the figure to a PNG image
    plt.savefig(file_path, format="png")
    plt.close()


# Function to plot the heatmap of routes and save as a PNG image
def plot_heatmap_of_routes(file_path: str):
    """
    Generates a heatmap for delayed flights by route (origin → destination) and saves it as a PNG image.

    Args:
        file_path: The path where the image will be saved.
    """
    query = """
    SELECT 
        flights.origin_airport AS origin,
        flights.destination_airport AS destination,
        COUNT(flights.id) AS total_flights,
        SUM(CASE WHEN flights.departure_delay > 20 THEN 1 ELSE 0 END) AS delayed_flights
    FROM flights
    GROUP BY origin, destination
    """
    df = pd.read_sql(query, engine)
    df['percent_delayed'] = (df['delayed_flights'] / df['total_flights']) * 100
    pivot_df = df.pivot(index='origin', columns='destination', values='percent_delayed')

    plt.figure(figsize=(9,8))
    sns.heatmap(pivot_df, cmap="Reds", linewidths=0.5)
    plt.title('Heatmap: % Delayed Flights by Route (Origin → Destination)')
    plt.ylabel('Origin Airport')
    plt.xlabel('Destination Airport')
    plt.tight_layout()

    # Save the figure to a PNG image
    plt.savefig(file_path, format="png")
    plt.close()


# Function to plot the map of routes and save as an HTML file
def plot_map_of_routes(file_path: str):
    """
    Generates and saves an interactive map of delayed flight routes across the USA.

    Args:
        file_path: The path where the HTML map will be saved.
    """
    query = """
    SELECT 
        flights.origin_airport AS origin,
        flights.destination_airport AS destination,
        COUNT(flights.id) AS total_flights,
        SUM(CASE WHEN flights.departure_delay > 20 THEN 1 ELSE 0 END) AS delayed_flights
    FROM flights
    GROUP BY origin, destination
    """

    df_routes = pd.read_sql(query, engine)
    df_routes['percent_delayed'] = (df_routes['delayed_flights'] / df_routes['total_flights']) * 100

    # Get airport coordinates
    query_airports = """
    SELECT IATA_CODE, LATITUDE, LONGITUDE
    FROM airports
    WHERE IATA_CODE IS NOT NULL
    """
    df_airports = pd.read_sql(query_airports, engine)
    airport_coords = df_airports.set_index('IATA_CODE')[['LATITUDE', 'LONGITUDE']].to_dict('index')

    # Create the base map
    flight_map = folium.Map(location=[39.8283, -98.5795], zoom_start=4)  # Center of USA

    # Draw routes
    for idx, row in df_routes.iterrows():
        origin = row['origin']
        dest = row['destination']
        delay_percent = row['percent_delayed']

        if origin not in airport_coords or dest not in airport_coords:
            continue  # Skip if coordinates are missing

        # Only show routes with delayed flights over 30%
        if delay_percent <= 30:
            continue  # Skip routes with low delay

        origin_coords = (float(airport_coords[origin]['LATITUDE']), float(airport_coords[origin]['LONGITUDE']))
        dest_coords = (float(airport_coords[dest]['LATITUDE']), float(airport_coords[dest]['LONGITUDE']))

        # Color logic (routes with higher delay are in red, lower in orange)
        color = 'red' if delay_percent > 50 else 'orange'

        folium.PolyLine(
            locations=[origin_coords, dest_coords],
            color=color,
            weight=1 + delay_percent / 40,  # Thicker for worse delay
            opacity=0.5,
            tooltip=f"{origin} → {dest}: {delay_percent:.1f}% delayed"
        ).add_to(flight_map)

    # Save the map as an HTML file
    flight_map.save(file_path)


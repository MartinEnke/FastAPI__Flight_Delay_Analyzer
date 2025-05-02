from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import List
import pandas as pd

DATABASE_URL = "sqlite:///flights.sqlite3"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FlightData:
    def __init__(self, db_session):
        self.db_session = db_session  # Accept the session object

    def _execute_query(self, query: str, params: dict):
        try:
            result = self.db_session.execute(text(query), params)
            return result.fetchall()
        except Exception as e:
            print("Database error:", e)
            return []

    def get_flight_by_id(self, flight_id: int):
        params = {'id': flight_id}
        query = """
        SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY 
        FROM flights 
        JOIN airlines ON flights.airline = airlines.id 
        WHERE flights.ID = :id
        """
        return self._execute_query(query, params)

    def get_flights_by_date(self, day: int, month: int, year: int):
        query = """
        SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY
        FROM flights
        JOIN airlines ON flights.airline = airlines.id
        WHERE flights.DAY = :day AND flights.MONTH = :month AND flights.YEAR = :year
        """
        params = {'day': day, 'month': month, 'year': year}
        return self._execute_query(query, params)

    def get_delayed_flights_by_airline(self, airline: str):
        params = {'airline': f"%{airline}%"}
        query = """
        SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY
        FROM flights
        JOIN airlines ON flights.airline = airlines.id
        WHERE airlines.airline LIKE :airline
        AND flights.DEPARTURE_DELAY > 20
        """
        return self._execute_query(query, params)

    def get_delayed_flights_by_airport(self, airport: str):
        params = {'airport': f"%{airport}%"}
        query = """
        SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY
        FROM flights
        JOIN airlines ON flights.airline = airlines.id
        WHERE flights.ORIGIN_AIRPORT LIKE :airport
        AND flights.DEPARTURE_DELAY > 20
        """
        return self._execute_query(query, params)

    def get_delayed_flights_by_hour(self):
        query = """
        SELECT 
            CAST(substr(flights.scheduled_departure, 1, 2) AS INTEGER) AS hour,
            COUNT(flights.id) AS total_flights,
            SUM(CASE WHEN flights.departure_delay > 20 THEN 1 ELSE 0 END) AS delayed_flights
        FROM flights
        GROUP BY hour
        ORDER BY hour
        """
        return self._execute_query(query, {})




# Function to plot the delays by airline
def plot_delays_by_airline():
    # Fetch the data (This is just an example, you should pass the data to the function)
    data = pd.DataFrame({
        'airline': ['Airline A', 'Airline B', 'Airline C'],
        'percent_delayed': [20, 25, 10]
    })

    # Plotting using Seaborn
    sns.barplot(x='airline', y='percent_delayed', data=data)
    plt.title('Percentage of Delayed Flights per Airline')
    plt.show()


# Function to plot the delays by hour
def plot_delays_by_hour():
    data = pd.DataFrame({
        'hour': [0, 1, 2, 3, 4],
        'percent_delayed': [15, 10, 25, 30, 20]
    })

    sns.barplot(x='hour', y='percent_delayed', data=data)
    plt.title('Percentage of Delayed Flights by Hour')
    plt.show()


# Function to plot the heatmap of routes
def plot_heatmap_of_routes():
    # Example data for heatmap
    data = pd.DataFrame({
        'route': ['A-B', 'B-C', 'C-D'],
        'delay_percentage': [10, 30, 25]
    })

    sns.heatmap(data.pivot("route", "delay_percentage"), annot=True, cmap="YlGnBu")
    plt.title('Heatmap of Delayed Flights by Route')
    plt.show()


# Function to plot map of routes (example with Folium or any other map tool)
def plot_map_of_routes():
    # Simple map for demonstration
    m = folium.Map(location=[37.7749, -122.4194], zoom_start=5)  # Example coordinates (San Francisco)
    folium.Marker([37.7749, -122.4194], popup="San Francisco").add_to(m)
    m.save("map.html")
    print("Map saved as map.html")



def get_db():
    """
    Returns the database session for FastAPI.
    """
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

# Dependency Injection Example for FastAPI (in routes)
# This can now be used in FastAPI route functions



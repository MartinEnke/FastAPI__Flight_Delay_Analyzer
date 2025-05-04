from sqlalchemy import create_engine, text

# Database URL
DATABASE_URL = "sqlite:///flights.sqlite3"
engine = create_engine(DATABASE_URL, echo=True)

# Example query
QUERY_FLIGHTS_BY_DATE = """
SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY
FROM flights
JOIN airlines ON flights.airline = airlines.id
WHERE flights.DAY = :day AND flights.MONTH = :month AND flights.YEAR = :year
"""

# Test the query
params = {'day': 1, 'month': 1, 'year': 2015}
with engine.connect() as conn:
    result = conn.execute(text(QUERY_FLIGHTS_BY_DATE), params)
    for row in result:
        print(row)
from typing import Optional
import visualization
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import data
from pydantic import BaseModel
from typing import List, Dict

# FastAPI app instance
app = FastAPI()

SQLITE_URI = 'sqlite:///flights.sqlite3'  # Using the correct SQLite URI
IATA_LENGTH = 3

# Pydantic response model for flight data
class FlightSearchResponse(BaseModel):
    FLIGHT_ID: int
    ORIGIN_AIRPORT: str
    DESTINATION_AIRPORT: str
    AIRLINE: str
    DELAY: Optional[int] = 0

@app.get("/", response_model=Dict[str, Dict[str, str]])
def home():
    return {
        "message": {"text": "Welcome to the Flight Delay Analyzer API!"},
        "available_endpoints": {
            "/delays_by_airline": "Get % of delayed flights by airline",
            "/delays_by_airport": "Get % of delayed flights by airport",
            "/flights_by_id": "Get flight details by ID",
            "/flights_by_date": "Get flights by date",
            "/delayed_flights_by_hour": "Get percentage of delayed flights by hour"
        },
        "status": {"text": "running"}
    }

def get_db():
    """Dependency to get the database session"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(SQLITE_URI, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

@app.get("/flight_by_id", response_model=FlightSearchResponse)
def flight_by_id(flight_id: int, db: Session = Depends(get_db)):
    try:
        data_manager = data.FlightData(db)  # Pass session to data manager
        results = data_manager.get_flight_by_id(flight_id)

        if not results:
            raise HTTPException(status_code=404, detail="Flight not found")

        return results[0]  # Return the first result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/delays_by_airline", response_model=List[FlightSearchResponse])
def delays_by_airline(airline: str, db: Session = Depends(get_db)):
    try:
        data_manager = data.FlightData(db)  # Pass session to data manager
        results = data_manager.get_delayed_flights_by_airline(airline)
        if not results:
            return []  # Return an empty list if no results found
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/flights_by_date", response_model=List[FlightSearchResponse])
def flights_by_date(date: str, db: Session = Depends(get_db)):
    try:
        date_input = datetime.strptime(date, '%d/%m/%Y')
    except ValueError:
        return {"error": "Invalid date format. Please provide a date in DD/MM/YYYY format."}

    data_manager = data.FlightData(db)  # Pass session to data manager
    results = data_manager.get_flights_by_date(date_input.day, date_input.month, date_input.year)
    return results

@app.get("/delayed_flights_by_hour", response_model=List[Dict[str, float]])
def delayed_flights_by_hour():
    data_manager = data.FlightData(SQLITE_URI)
    results = data_manager.get_delayed_flights_by_hour()
    return results


@app.get("/show_bar_graph")
def show_bar_graph():
    """
    API endpoint: Displays the bar graph for percentage of delayed flights per airline.
    """
    visualization.plot_delays_by_airline()
    return {"message": "Bar graph for delayed flights per airline displayed"}

@app.get("/show_hourly_bar_graph")
def show_hourly_bar_graph():
    """
    API endpoint: Displays a bar graph showing the percentage of delayed flights by hour of the day.
    """
    visualization.plot_delays_by_hour()
    return {"message": "Bar graph for delayed flights by hour displayed"}

@app.get("/show_heatmap_of_routes")
def show_heatmap_of_routes():
    """
    API endpoint: Displays a heatmap showing the percentage of delayed flights distributed across flight routes.
    """
    visualization.plot_heatmap_of_routes()
    return {"message": "Heatmap of delayed flights by route displayed"}

@app.get("/show_map_of_routes")
def show_map_of_routes():
    """
    API endpoint: Displays a map showing major delayed routes across the USA.
    """
    visualization.plot_map_of_routes()
    return {"message": "Map of delayed routes displayed"}

# To run the FastAPI app in a development environment:
# uvicorn main:app --reload

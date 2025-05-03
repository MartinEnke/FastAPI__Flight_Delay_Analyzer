from typing import Optional, List, Dict
import visualization
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import data
from pydantic import BaseModel
from fastapi.responses import FileResponse, Response
import os
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from fastapi.middleware.cors import CORSMiddleware


# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware to allow cross-origin requests (useful when frontend and backend are on different origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing or configure specific ones
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        data_manager = data.FlightData(db)
        results = data_manager.get_flight_by_id(flight_id)
        if not results:
            raise HTTPException(status_code=404, detail="Flight not found")
        return results[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/delays_by_airline", response_model=List[FlightSearchResponse])
def delays_by_airline(airline: str, db: Session = Depends(get_db)):
    try:
        data_manager = data.FlightData(db)
        results = data_manager.get_delayed_flights_by_airline(airline)
        if not results:
            return []
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/delays_by_airport", response_model=List[FlightSearchResponse])
def delays_by_airport(airport_code: str, db: Session = Depends(get_db)):
    if len(airport_code) != IATA_LENGTH or not airport_code.isalpha():
        raise HTTPException(status_code=400, detail="Invalid IATA code. Please provide a valid 3-letter airport code.")
    data_manager = data.FlightData(db)
    results = data_manager.get_delayed_flights_by_airport(airport_code)
    return results


@app.get("/flights_by_date", response_model=List[FlightSearchResponse])
def flights_by_date(date: str, db: Session = Depends(get_db)):
    try:
        date_input = datetime.strptime(date, '%d/%m/%Y')
    except ValueError:
        return {"error": "Invalid date format. Please provide a date in DD/MM/YYYY format."}
    data_manager = data.FlightData(db)
    results = data_manager.get_flights_by_date(date_input.day, date_input.month, date_input.year)
    return results


@app.get("/delayed_flights_by_hour", response_model=List[Dict[str, float]])
def delayed_flights_by_hour(hour: Optional[int] = None, threshold: Optional[int] = 20, db: Session = Depends(get_db)):
    try:
        data_manager = data.FlightData(db)
        results = data_manager.get_delayed_flights_by_hour(threshold)
        if not results:
            return []
        if hour is not None:
            results = [r for r in results if r['hour'] == hour]
        return results
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/show_bar_graph", responses={200: {"content": {"image/png": {}}}})
def show_bar_graph():
    """
    API endpoint: Generates and returns the bar graph for percentage of delayed flights per airline as a PNG image.
    """
    # Create the graph in memory
    fig = visualization.plot_delays_by_airline()

    # Convert the plot to bytes in memory
    buf = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buf)
    buf.seek(0)  # Move to the start of the BytesIO buffer

    # Return the image as a response
    return Response(content=buf.read(), media_type="image/png")


@app.get("/show_hourly_bar_graph", responses={200: {"content": {"image/png": {}}}})
def show_hourly_bar_graph():
    """
    Generates and returns the bar graph for percentage of delayed flights per hour as a PNG image.
    """
    # Create the graph in memory
    fig = visualization.plot_delays_by_hour()

    # Convert the plot to bytes in memory
    buf = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buf)
    buf.seek(0)  # Move to the start of the BytesIO buffer

    # Return the image as a response
    return Response(content=buf.read(), media_type="image/png")


@app.get("/show_heatmap_of_routes", responses={200: {"content": {"image/png": {}}}})
def show_heatmap_of_routes():
    """
    API endpoint: Generates and returns a heatmap showing the percentage of delayed flights distributed across flight routes as a PNG image.
    """
    # Create the heatmap in memory
    fig = visualization.plot_heatmap_of_routes()

    # Convert the plot to bytes in memory
    buf = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buf)
    buf.seek(0)  # Move to the start of the BytesIO buffer

    # Return the image as a response
    return Response(content=buf.read(), media_type="image/png")


@app.get("/show_map_of_routes")
def show_map_of_routes():
    """
    API endpoint: Generates and saves a map showing major delayed routes across the USA.
    """
    file_path = "static/maps/map_of_routes.html"
    visualization.plot_map_of_routes(file_path)

    # Return the file as a response, but the proper MIME type for HTML files
    return FileResponse(file_path, media_type="text/html")


# To run the FastAPI app in a development environment:
# uvicorn main:app --reload
# http://127.0.0.1:8000/docs

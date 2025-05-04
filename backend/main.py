import data
import visualization
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
import os

STATIC_FOLDER = "static/graphs"
os.makedirs(STATIC_FOLDER, exist_ok=True)


# Initialize FastAPI app
app = FastAPI()

# Mount static directories for graphs and maps
app.mount("/static/graphs", StaticFiles(directory="static/graphs"), name="graphs")
app.mount("/static/maps", StaticFiles(directory="static/maps"), name="maps")

# Add CORS middleware to allow cross-origin requests (useful when frontend and backend are on different origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing or configure specific ones
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Folder to save images
STATIC_FOLDER = "static/graphs"
os.makedirs(STATIC_FOLDER, exist_ok=True)

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
    """
    Home endpoint providing general information and available API endpoints.

    Returns:
        A dictionary containing the status message and available endpoints.
    """
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
    """
    Dependency to get the database session.

    Returns:
        A database session object.
    """
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
    """
    Fetches flight details by flight ID.

    Args:
        flight_id: The ID of the flight to be retrieved.

    Returns:
        Flight details as a response.
    """
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
    """
    Fetches delayed flights by airline.

    Args:
        airline: The name of the airline.

    Returns:
        A list of delayed flight details for the specified airline.
    """
    try:
        data_manager = data.FlightData(db)
        results = data_manager.get_delayed_flights_by_airline(airline)
        if not results:
            return []  # Return an empty list if no results found
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/delays_by_airport", response_model=List[FlightSearchResponse])
def delays_by_airport(airport_code: str, db: Session = Depends(get_db)):
    """
    Fetches delayed flights by airport code (IATA).

    Args:
        airport_code: The IATA code of the airport.

    Returns:
        A list of delayed flight details for the specified airport.
    """
    if len(airport_code) != IATA_LENGTH or not airport_code.isalpha():
        raise HTTPException(status_code=400, detail="Invalid IATA code. Please provide a valid 3-letter airport code.")

    data_manager = data.FlightData(db)
    results = data_manager.get_delayed_flights_by_airport(airport_code)
    return results


@app.get("/flights_by_date", response_model=List[FlightSearchResponse])
def flights_by_date(date: str, db: Session = Depends(get_db)):
    """
    Fetches flights by a specific date.

    Args:
        date: The date to fetch flights for, in the format 'DD/MM/YYYY'.

    Returns:
        A list of flight details for the specified date.
    """
    try:
        date_input = datetime.strptime(date, '%d/%m/%Y')
    except ValueError:
        return {"error": "Invalid date format. Please provide a date in DD/MM/YYYY format."}

    data_manager = data.FlightData(db)
    results = data_manager.get_flights_by_date(date_input.day, date_input.month, date_input.year)
    return results


@app.get("/delayed_flights_by_hour", response_model=List[Dict[str, float]])
def delayed_flights_by_hour(hour: Optional[int] = None, threshold: Optional[int] = 20, db: Session = Depends(get_db)):
    """
    Fetches the percentage of delayed flights by hour, with an optional threshold for delays.

    Args:
        hour: The hour to filter by (optional).
        threshold: The minimum delay threshold to filter by (default is 20 minutes).

    Returns:
        A list of delayed flights by hour, optionally filtered by hour and delay threshold.
    """
    try:
        data_manager = data.FlightData(db)
        results = data_manager.get_delayed_flights_by_hour(threshold)
        if not results:
            return []

        # Optional filtering based on hour
        if hour is not None:
            results = [r for r in results if r['hour'] == hour]

        return results
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


def generate_plot_for_delay_by_hours(file_path: str):
    """
    Generates a plot and saves it as a PNG file at the specified path.

    Args:
        file_path: The path where the generated plot will be saved.
    """
    # Generate the plot (your plotting function)
    fig = visualization.plot_delays_by_hour()  # Assuming this returns a matplotlib figure

    # Convert plot to bytes
    buf = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buf)
    buf.seek(0)

    # Save the plot as a file in the static directory
    with open(file_path, 'wb') as f:
        f.write(buf.read())


@app.get("/show_bar_graph", responses={200: {"content": {"image/png": {}}}})
def show_bar_graph():
    """
    Generates and returns the bar graph for percentage of delayed flights per airline as a PNG image.
    The image is also saved to the static folder for later access.
    """
    # Create the graph in memory
    fig = visualization.plot_delays_by_airline()

    # Convert the plot to bytes in memory
    buf = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buf)
    buf.seek(0)  # Move to the start of the BytesIO buffer

    # Save the image to static folder
    file_path = os.path.join(STATIC_FOLDER, "bar_graph.png")
    with open(file_path, "wb") as f:
        f.write(buf.read())

    # Return a message with image and confirmation
    return JSONResponse(content={
        "message": "Graph 'bar_graph.png' has been successfully generated and saved in the static folder.",
        "image_url": f"/static/graphs/bar_graph.png"
    })



@app.get("/show_hourly_bar_graph")
async def show_hourly_bar_graph(background_tasks: BackgroundTasks):
    """
    Initiates graph generation in the background for hourly delays.
    Returns a response indicating the task is in progress.

    Args:
        background_tasks: A background task object to execute the task asynchronously.

    Returns:
        A message indicating the graph generation is in progress.
    """
    file_path = os.path.join(STATIC_FOLDER, "hourly_bar_graph.png")

    # Add the task to generate the graph in the background
    background_tasks.add_task(generate_plot_for_delay_by_hours, file_path)

    # Return a response indicating that the graph generation is in progress
    return {"message": "Graph is generated in the background and successfully saved in the static folder.",
            "image_url": "/static/graphs/hourly_bar_graph.png"}


@app.get("/show_heatmap_of_routes", responses={200: {"content": {"image/png": {}}}})
def show_heatmap_of_routes():
    """
    Generates and returns a heatmap showing the percentage of delayed flights distributed across flight routes as a PNG image.
    The image is also saved to the static folder for later access.
    """
    # Create the heatmap in memory
    fig = visualization.plot_heatmap_of_routes()

    # Convert the plot to bytes in memory
    buf = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buf)
    buf.seek(0)  # Move to the start of the BytesIO buffer

    # Save the image to static folder
    file_path = os.path.join(STATIC_FOLDER, "heatmap_of_routes.png")
    with open(file_path, "wb") as f:
        f.write(buf.read())

    # Return a message with image and confirmation
    return JSONResponse(content={
        "message": "Heatmap 'heatmap_of_routes.png' has been successfully generated and saved in the static folder.",
        "image_url": f"/static/graphs/heatmap_of_routes.png"
    })


@app.get("/show_map_of_routes")
def show_map_of_routes():
    """
    Generates and saves an interactive map showing major delayed routes across the USA.
    The map is saved as an HTML file in the static folder.
    """
    file_path = "static/maps/map_of_routes.html"
    visualization.plot_map_of_routes(file_path)

    # Return the file as a response, but the proper MIME type for HTML files
    return FileResponse(file_path, media_type="text/html")



# To run the FastAPI app in a development environment:
# uvicorn main:app --reload
# http://127.0.0.1:8000/docs
# http://127.0.0.1:8000/redoc

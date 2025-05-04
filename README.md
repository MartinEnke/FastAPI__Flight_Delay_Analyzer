# FastAPI - Flight Delay Analyzer

**FastAPI version of the Flight Delay Analyzer** project. 
This web application allows users to search for flight delay data based on various parameters such as flight ID, airline, airport, and hour. 
It interacts with a FastAPI backend to fetch the data and displays the results in a user-friendly interface.

<img src="banner.png" alt="Flight Delay Analyzer Banner" 
## Technologies Used

### Tools:
- ![PyCharm](https://img.shields.io/badge/PyCharm-%000000.svg?style=flat&logo=pycharm&logoColor=white) - Python IDE used for development.
- ![GitHub](https://img.shields.io/badge/GitHub-%23121011.svg?style=flat&logo=github&logoColor=white) - For version control and collaboration.
- ![Visual Studio Code](https://img.shields.io/badge/VS_Code-%23007ACC.svg?style=flat&logo=visualstudiocode&logoColor=white) - IDE used for development.
- ![Postman](https://img.shields.io/badge/Postman-%23FF6C37.svg?style=flat&logo=postman&logoColor=white) - Tool for testing API requests.

### Backend:

- ![FastAPI](https://img.shields.io/badge/FastAPI-%2300C7B7.svg?style=flat&logo=fastapi&logoColor=white) - Backend framework used for building the API.
- ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-%23016E0D.svg?style=flat&logo=sqlalchemy&logoColor=white) - ORM for interacting with the database.
- ![Pydantic](https://img.shields.io/badge/Pydantic-%2302D28C.svg?style=flat&logo=pydantic&logoColor=white) - Data validation library.
- ![SQLite](https://img.shields.io/badge/SQLite-%2307401C.svg?style=flat&logo=sqlite&logoColor=white) - Lightweight database used to store flight data.
- ![CORS Middleware](https://img.shields.io/badge/CORS_Middleware-%2388888B.svg?style=flat&logo=cors&logoColor=white) - Middleware for handling cross-origin requests.

### Frontend:

- ![HTML5](https://img.shields.io/badge/HTML5-%23E34F26.svg?style=flat&logo=html5&logoColor=white) - Used for structuring the web pages.
- ![CSS3](https://img.shields.io/badge/CSS3-%231572B6.svg?style=flat&logo=css3&logoColor=white) - Styling the web pages.
- ![JavaScript](https://img.shields.io/badge/JavaScript-%23F7DF1E.svg?style=flat&logo=javascript&logoColor=black) - Used for handling dynamic content and user interactions.
- ![Fetch API](https://img.shields.io/badge/Fetch_API-%233547A5.svg?style=flat&logo=fetch&logoColor=white) - Used for making HTTP requests.


### Graphics and Visualization:

- ![Matplotlib](https://img.shields.io/badge/Matplotlib-%23E04E39.svg?style=flat&logo=matplotlib&logoColor=white) - Library used for generating plots and graphs.

## Features

- **Search Flights by ID**: Search for a specific flight's details based on its flight ID.
- **Search Flights by Airline**: View flights and their delays by airline.
- **Search Flights by Airport**: Search for delayed flights originating from a specific airport.
- **Search Flights by Hour**: Filter flights based on a specific hour of the day.
- **Flight Visualizations**: Visualize delayed flights by airlines, by hour, and on a route heatmap.

## Setup Instructions

### Prerequisites
Make sure you have the following installed:

- **Python 3.x**
- **Node.js** (if you plan to run a frontend server separately)

### 1. Backend Setup
Clone the repository and install the backend dependencies.

```
git clone https://github.com/yourusername/flight-delay-analyzer.git
cd flight-delay-analyzer
pip install -r requirements.txt
```
### 2. Database Setup
Make sure the SQLite database is properly set up by running the necessary migrations (if applicable).

### 3. Start the Backend Server
rn main:app --reload

### 4. Frontend Setup
You may need to adjust the frontend files to connect to the appropriate backend endpoint. Ensure that the correct apiUrl is set in the frontend JavaScript.

### 5. Open the Web Application
Once everything is set up, navigate to http://localhost:8000 in your browser to view the web application.


Acknowledgments
Thanks to FastAPI for providing a fast and modern web framework for Python.
Thanks to Matplotlib for helping us create beautiful visualizations for the project.
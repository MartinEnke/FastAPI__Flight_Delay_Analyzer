const apiUrl = "http://127.0.0.1:8000";  // The backend API URL

// Define the content for each section
const contentMap = {
  "id": {
    title: "Search Flight by ID",
    placeholder: "Enter Flight ID",
    subtitle: "Flight by Flight ID",
    endpoint: "/flight_by_id"
  },
  "airline": {
    title: "Search Flights by Airline",
    placeholder: "Enter Airline Name",
    subtitle: "Flights by Airline",
    endpoint: "/delays_by_airline"
  },
  "airport": {
    title: "Search Flights by Airport",
    placeholder: "Enter Airport IATA",
    subtitle: "Flights by Airport",
    endpoint: "/delays_by_airport"
  },
  "hour": {
    title: "Search Flights by Hour",
    placeholder: "Enter Hour (0-23)",
    subtitle: "Flights by Hour",
    endpoint: "/delayed_flights_by_hour"
  },
  "delays-airlines": {
    title: "Flight Delays by Airline",
    placeholder: "Enter Airline (optional)",
    subtitle: "Delayed Flights by Airline",
    endpoint: "/delays_by_airline"
  },
  "delays-hour": {
    title: "Flight Delays by Hour",
    placeholder: "Enter Hour (0-23)",
    subtitle: "Delayed Flights by Hour",
    endpoint: "/delayed_flights_by_hour"
  },
  "delays-routes": {
    title: "Flight Delays by Routes",
    placeholder: "Enter Route",
    subtitle: "Delayed Flights by Routes",
    endpoint: "/delays_by_airport"
  },
  "heatmap-routes": {
    title: "Flight Delays Heatmap by Routes",
    placeholder: "Enter Parameters",
    subtitle: "Flight Delays Heatmap",
    endpoint: "/show_heatmap_of_routes"
  }
};

// Grab references to the elements we need to update
const searchTitleEl = document.getElementById('search-title');
const searchInputEl = document.getElementById('search-input');
const bottomLabelEl = document.getElementById('bottom-label');
const resultsContainer = document.getElementById('results-container');

// Function to fetch data from the backend
async function fetchData(endpoint, params) {
  const url = new URL(apiUrl + endpoint);
  if (params) {
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
  }
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('Failed to fetch data');
  }
  return response.json();
}

// Function to display the results
function displayResults(data) {
  // Clear existing results
  resultsContainer.innerHTML = '';

  // Check if there is data
  if (Array.isArray(data) && data.length > 0) {
    data.slice(0, 10).forEach(result => {
      const resultItem = document.createElement('div');
      resultItem.classList.add('result-item');
      resultItem.textContent = JSON.stringify(result, null, 2); // Display data as JSON for now
      resultsContainer.appendChild(resultItem);
    });
  } else {
    resultsContainer.innerHTML = '<p>No results found.</p>';
  }
}

// Attach click event listeners to each sidebar link
document.querySelectorAll('#menu a[data-section]').forEach(link => {
  link.addEventListener('click', event => {
    event.preventDefault();  // Prevent default link behavior
    const section = link.getAttribute('data-section');

    // Update the main content (title, placeholder, subtitle)
    if (contentMap[section]) {
      searchTitleEl.textContent = contentMap[section].title;
      searchInputEl.setAttribute('placeholder', contentMap[section].placeholder);
      bottomLabelEl.textContent = contentMap[section].subtitle;
    }
  });
});


// Attach keydown event listener to the search input field
document.getElementById('search-input').addEventListener('keydown', async (event) => {
  // Check if the 'Enter' key (key code 13) is pressed
  if (event.key === 'Enter') {
    const section = document.querySelector('#menu a.active').getAttribute('data-section'); // Get selected section
    const userInput = event.target.value.trim();

    // Make sure the user input is not empty before making the request
    if (!userInput) {
      alert('Please enter a value to search.');
      return;
    }

    try {
      let params = {};
      if (section === 'id') {
        params = { flight_id: userInput }; // Use user input as flight ID
      } else if (section === 'airline') {
        params = { airline: userInput }; // Use user input as airline
      } else if (section === 'airport') {
        params = { airport_code: userInput }; // Use user input as airport code
      } else if (section === 'hour') {
        params = { hour: userInput }; // Use user input as hour
      }

      const data = await fetchData(contentMap[section].endpoint, params);
      displayResults(data); // Display the results in the results container
    } catch (error) {
      resultsContainer.innerHTML = "Error fetching data: " + error.message;
    }
  }
});

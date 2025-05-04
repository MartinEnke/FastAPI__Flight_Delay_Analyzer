const apiUrl = "http://127.0.0.1:8000";  // Replace with your API URL

// Fetch flight by ID
function getFlightById() {
    const flightId = document.getElementById("flight-id").value;
    fetch(`${apiUrl}/flight_by_id?flight_id=${flightId}`)
        .then(response => response.json())
        .then(data => {
            if (data.FLIGHT_ID) {
                document.getElementById("flight-info").innerHTML = `
                    <p><strong>Flight ID:</strong> ${data.FLIGHT_ID}</p>
                    <p><strong>Origin Airport:</strong> ${data.ORIGIN_AIRPORT}</p>
                    <p><strong>Destination Airport:</strong> ${data.DESTINATION_AIRPORT}</p>
                    <p><strong>Airline:</strong> ${data.AIRLINE}</p>
                    <p><strong>Delay:</strong> ${data.DELAY} minutes</p>
                `;
            } else {
                document.getElementById("flight-info").innerHTML = `<p>No flight found.</p>`;
            }
        })
        .catch(error => {
            document.getElementById("flight-info").innerHTML = `<p>Error fetching data. Please try again later.</p>`;
        });
}

// Fetch delayed flights by airline
function getDelaysByAirline() {
    const airline = document.getElementById("airline-name").value;
    fetch(`${apiUrl}/delays_by_airline?airline=${airline}`)
        .then(response => response.json())
        .then(data => {
            let delaysHtml = "";
            if (data.length > 0) {
                data.forEach(flight => {
                    delaysHtml += `
                        <p><strong>Flight ID:</strong> ${flight.FLIGHT_ID} - <strong>Delay:</strong> ${flight.DELAY} minutes</p>
                    `;
                });
                document.getElementById("delays-by-airline").innerHTML = delaysHtml;
            } else {
                document.getElementById("delays-by-airline").innerHTML = `<p>No delays found for the airline.</p>`;
            }
        })
        .catch(error => {
            document.getElementById("delays-by-airline").innerHTML = `<p>Error fetching data. Please try again later.</p>`;
        });
}


// Fetch delayed flights by airport
function getDelaysByAirport() {
    const airportCode = document.getElementById("airport-name").value;
    fetch(`${apiUrl}/delays_by_airport?airport_code=${airportCode}`)
        .then(response => response.json())
        .then(data => {
            let delaysHtml = "";
            if (data.length > 0) {
                data.forEach(flight => {
                    delaysHtml += `
                        <p><strong>Flight ID:</strong> ${flight.FLIGHT_ID} - <strong>Delay:</strong> ${flight.DELAY} minutes</p>
                    `;
                });
                document.getElementById("delays-by-airport").innerHTML = delaysHtml;
            } else {
                document.getElementById("delays-by-airport").innerHTML = `<p>No delays found for the airport.</p>`;
            }
        })
        .catch(error => {
            document.getElementById("delays-by-airport").innerHTML = `<p>Error fetching data. Please try again later.</p>`;
        });
}

// Get flights by date
function getFlightsByDate() {
    const date = document.getElementById("flight-date").value;
    fetch(`${apiUrl}/flights_by_date?date=${date}`)
        .then(response => response.json())
        .then(data => {
            let flightsHtml = "";
            if (data.length > 0) {
                data.forEach(flight => {
                    flightsHtml += `
                        <p><strong>Flight ID:</strong> ${flight.FLIGHT_ID} - <strong>Delay:</strong> ${flight.DELAY} minutes</p>
                    `;
                });
                document.getElementById("flights-by-date").innerHTML = flightsHtml;
            } else {
                document.getElementById("flights-by-date").innerHTML = `<p>No flights found for the date.</p>`;
            }
        })
        .catch(error => {
            document.getElementById("flights-by-date").innerHTML = `<p>Error fetching data. Please try again later.</p>`;
        });
}

// Get delayed flights by hour
function getDelayedFlightsByHour() {
    const hour = document.getElementById("hour").value;
    fetch(`${apiUrl}/delayed_flights_by_hour?hour=${hour}`)
        .then(response => response.json())
        .then(data => {
            let delayedHtml = "";
            if (data.length > 0) {
                data.forEach(flight => {
                    delayedHtml += `
                        <p><strong>Hour:</strong> ${flight.hour} - <strong>Delay:</strong> ${flight.percent_delayed}%</p>
                    `;
                });
                document.getElementById("delayed-by-hour").innerHTML = delayedHtml;
            } else {
                document.getElementById("delayed-by-hour").innerHTML = `<p>No delayed flights found for the hour.</p>`;
            }
        })
        .catch(error => {
            document.getElementById("delayed-by-hour").innerHTML = `<p>Error fetching data. Please try again later.</p>`;
        });
}

// Generate Delay by Airline Graph
function generateGraph() {
    fetch(`${apiUrl}/show_bar_graph`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("graph-message").innerHTML = data.message;
            const imageUrl = data.image_url;  // Example: /static/graphs/bar_graph.png
            const img = new Image();
            img.src = "http://127.0.0.1:8000" + imageUrl;  // Full URL will be used by the browser
            img.onload = function() {
                document.getElementById("graph-container").innerHTML = ''; // Clear any previous content
                document.getElementById("graph-container").appendChild(img); // Add the new graph image
            };
            img.onerror = function() {
                document.getElementById("graph-message").innerHTML = `<p>Error loading graph image.</p>`;
            };
        })
        .catch(error => {
            document.getElementById("graph-message").innerHTML = `<p>Error generating graph. Please try again later.</p>`;
        });
}

// Generate Heatmap
function generateHeatmap() {
    fetch(`${apiUrl}/show_heatmap_of_routes`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("graph-message").innerHTML = data.message;
            const imageUrl = data.image_url;  // Example: /static/graphs/heatmap_of_routes.png
            console.log('Heatmap image URL:', imageUrl);

            const img = new Image();
            img.src = "http://127.0.0.1:8000" + imageUrl;  // Full URL will be used by the browser
            img.onload = function() {
                document.getElementById("graph-container").innerHTML = ''; // Clear any previous content
                document.getElementById("graph-container").appendChild(img); // Add the new heatmap image
            };
            img.onerror = function() {
                document.getElementById("graph-message").innerHTML = `<p>Error loading heatmap image.</p>`;
            };
        })
        .catch(error => {
            document.getElementById("graph-message").innerHTML = `<p>Error generating heatmap. Please try again later.</p>`;
        });
}

// Show Map of Routes
function showMap() {
    const mapUrl = `${apiUrl}/show_map_of_routes`;  // URL to fetch map HTML
    window.open(mapUrl, "_blank");  // Open the map in a new tab
}
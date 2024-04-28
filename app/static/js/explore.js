// Create a map instance
var map = L.map('map').setView([49, 50], 3); // Set initial coordinates and higher zoom level

// Add a tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Create a marker cluster group
var markers = L.markerClusterGroup();

// Function to refresh map and perform search
function searchAndRefreshMap() {
    // Clear existing markers
    markers.clearLayers();
    
    // Fetch data from backend API based on selected filters and search query
    var networkType = document.getElementById('networkType').value;
    var encryption = document.getElementById('encryption').value;
    var searchQueryName = document.getElementById('searchInputName').value.trim();
    var searchQueryNetworkId = document.getElementById('searchInputNetworkId').value.trim();
    var excludeNoSSID = document.getElementById('excludeNoSSID').checked; // New checkbox to exclude "(no SSID)"

    // Construct URL with filters
    var url = '/api/explore';
    var filters = [];

    // Add filters based on selected options and search queries
    if (networkType) {
        filters.push('network_type=' + networkType);
    }
    if (encryption) {
        filters.push('encryption=' + encryption);
    }
    if (searchQueryName) {
        filters.push('name=' + encodeURIComponent(searchQueryName));
    }
    if (searchQueryNetworkId) {
        filters.push('network_id=' + encodeURIComponent(searchQueryNetworkId));
    }

    // If checkbox is checked, add a filter to exclude entries with the name "(no SSID)"
    if (excludeNoSSID) {
        filters.push('exclude_no_ssid=true');
    }

    // Append filters to the URL if any are set
    if (filters.length > 0) {
        url += '?' + filters.join('&');
    }
    
    // Fetch data from API
    fetch(url)
    .then(response => response.json())
    .then(data => {
        // Loop through the data and add markers to the cluster group
        data.forEach(poi => {
            // Create popup content with the desired fields
            var popupContent = `
                <strong>Name:</strong> ${poi.name}<br>
                <strong>Network ID:</strong> ${poi.network_id}<br>
                <strong>Encryption:</strong> ${poi.encryption}<br>
                <strong>Time:</strong> ${poi.time}<br>
                <strong>Signal:</strong> ${poi.signal}<br>
                <strong>Accuracy:</strong> ${poi.accuracy}<br>
                <strong>Network Type:</strong> ${poi.network_type}<br>
            `;
            // Create a marker and bind popup with the custom content
            var marker = L.marker([poi.latitude, poi.longitude]).bindPopup(popupContent);
            markers.addLayer(marker); // Add marker to the cluster group
        });

        // Add the marker cluster group to the map
        map.addLayer(markers);
        
        // If there are results, center map on the first result with default zoom
        if (data.length > 0) {
            map.setView([data[0].latitude, data[0].longitude], 15);
        }
    })
    .catch(error => console.error('Error fetching data:', error));
}

// Call searchAndRefreshMap function initially to load data

// Add event listeners for Enter key in search fields
document.getElementById('searchInputName').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        searchAndRefreshMap();
    }
});

// Add event listeners for pressing Enter key in the search field for network ID
document.getElementById('searchInputNetworkId').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        searchAndRefreshMap();
    }
});

// Add event listener to search button
document.getElementById('searchButton').addEventListener('click', function() {
    searchAndRefreshMap();
});


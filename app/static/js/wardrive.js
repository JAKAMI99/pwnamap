// Initialize the Leaflet map
var map = L.map('map').setView([51.3, 7.3], 12); // Example starting point (Berlin, Germany)

// Add a tile layer (OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 18,
}).addTo(map);

// Function to linearly interpolate between two colors
function interpolateColor(startColor, endColor, factor) {
    var result = startColor.slice();
    for (var i = 0; i < 3; i++) {
        result[i] = Math.round(result[i] + factor * (endColor[i] - startColor[i]));
    }
    return `rgb(${result[0]}, ${result[1]}, ${result[2]})`;
}

// Function to determine the gradient color based on distance
function getGradientColor(distance, minDistance, maxDistance, startColor, endColor) {
    if (distance <= minDistance) {
        return `rgb(${startColor[0]}, ${startColor[1]}, ${startColor[2]})`;
    }
    if (distance >= maxDistance) {
        return `rgb(${endColor[0]}, ${endColor[1]}, ${endColor[2]})`;
    }
    var factor = (distance - minDistance) / (maxDistance - minDistance);
    return interpolateColor(startColor, endColor, factor);
}

// Function to calculate the distance from a point to the nearest street
function distanceToNearestStreet(point, streetLayer) {
    var minDistance = Infinity;
    streetLayer.eachLayer(function (layer) {
        var streetCoords = layer.feature.geometry.coordinates;
        var distance = turf.pointToLineDistance(
            turf.point([point.getLatLng().lat, point.getLatLng().lng]), 
            streetCoords,
            { units: 'meters' }
        );
        if (distance < minDistance) {
            minDistance = distance;
        }
    });
    return minDistance;
}

// Function to apply styles to streets based on proximity to data points with a linear gradient
function styleStreets(streetLayer, markers, minDistance, maxDistance, startColor, endColor) {
    streetLayer.eachLayer(function (layer) {
        var centroid = turf.centroid(layer.feature); // Get centroid of the street segment
        var distances = markers.map(marker => distanceToNearestStreet(marker, streetLayer)); // Calculate distances
        var closestDistance = Math.min(...distances);

        var color = getGradientColor(closestDistance, minDistance, maxDistance, startColor, endColor); // Get gradient color
        layer.setStyle({
            color: color,
            weight: 3,
        });
    });
}

// Function to fetch GeoJSON street data from Overpass Turbo API
function fetchStreetData(bbox, query) {
    const overpassUrl = "hhttps://overpass-api.de/api/interprete";
    const queryBody = `
        [bbox:${bbox}]
        [out:json]
        [timeout:90];
        (${query});
        out geom;
    `;
    return fetch(overpassUrl, {
        method: "POST",
        body: "data=" + encodeURIComponent(queryBody),
    })
    .then(response => response.json())
    .catch(error => console.error("Error fetching data from Overpass:", error));
}


// Function to fetch datapoints and display on map
function loadDataPoints(apiUrl, map) {
    return fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            var markers = [];
            data.forEach(point => {
                var marker = L.marker([point.latitude, point.longitude]);
                markers.push(marker);
                marker.addTo(map);
            });
            return markers; // Return an array of Leaflet markers
        })
        .catch(error => console.error("Error fetching data points:", error));
}

// Set the range for the gradient (in meters)
var minDistance = 0; // Closest point is at distance 0 meters
var maxDistance = 200; // Farthest point before reaching max color
// Start and end colors for the gradient (from green to red)
var startColor = [0, 255, 0]; // Green
var endColor = [255, 0, 0]; // Red

// Fetch street data from Overpass Turbo and apply gradient style
var bbox = "52.50,13.39,52.54,13.42"; // Bounding box for Berlin, Germany
var overpassQuery = "way[highway];"; // Query to get all streets with the "highway" tag

fetchStreetData(bbox, overpassQuery).then((streetLayerData) => {
    var streetLayer = L.geoJSON(streetLayerData).addTo(map); // Add GeoJSON street data to map

    // Fetch datapoints and style streets
    var dataPointsApiUrl = '/api/explore'; // Your existing endpoint for datapoints
    loadDataPoints(dataPointsApiUrl, map).then((markers) => {
        styleStreets(streetLayer, markers, minDistance, maxDistance, startColor, endColor); // Apply gradient style to streets
    });
});

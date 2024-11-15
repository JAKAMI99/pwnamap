function generateGeoSchemeURL(latitude, longitude) {
  return `geo:${latitude},${longitude}`;
}

function generateWifiUriScheme(ssid, encryption, password) {
  return `WIFI:S:${ssid};T:${encryption};P:${password};H:false;`;
}

function createQRCode(data) {
  var qr = qrcode(0, 'M'); // Error correction level
  qr.addData(data);
  qr.make();
  return qr.createDataURL(10, 0); // Size and margin
}

function generateQrCode(wifiUri) {
  var qrCodeUrl = createQRCode(wifiUri);
  window.open(qrCodeUrl, '_blank');
}

var map = L.map('map').setView([0, 0], 2);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors',
  maxZoom: 24
}).addTo(map);

L.control.locate({ drawCircle: false }).addTo(map);

fetch('/api/pwnamap')
  .then((response) => response.json())
  .then((data) => {
    let totalLat = 0;
    let totalLng = 0;
    let count = data.length;

    data.forEach((poi) => {
      totalLat += poi.latitude;
      totalLng += poi.longitude;
    });

    let avgLat = totalLat / count;
    let avgLng = totalLng / count;

    if (!Number.isNaN(avgLat) && !Number.isNaN(avgLng)) {
      map.setView([avgLat, avgLng], 10);
    }

    data.forEach((poi) => {
      var radius = poi.accuracy ?? 0;

      var geoSchemeURL = generateGeoSchemeURL(poi.latitude, poi.longitude);
      poi.wifiUri = generateWifiUriScheme(poi.name, poi.encryption, poi.password);

      var circle = L.circle([poi.latitude, poi.longitude], {
        radius: radius,
        color: '#fc0865',
        weight: 2,
        fill: false,
      });

      var marker = L.marker([poi.latitude, poi.longitude]);

      var popupContent = `
        <strong>Name:</strong> ${poi.name}<br>
        <strong>Password:</strong> ${poi.password}<br>
        <strong>Accuracy:</strong> ${poi.accuracy} meters<br>
        <button onclick="window.open('${geoSchemeURL}', '_blank')">Navigate to</button><button onclick="generateQrCode('${poi.wifiUri}')">Show QR</button><br>
      `;

      marker.addTo(map).bindPopup(popupContent);

      marker.on("click", function() {
        map.setView([poi.latitude, poi.longitude], 19); // Center and zoom in on click
        map.addLayer(circle); // Add circle when the marker is clicked
      });

      marker.on("popupclose", function() {
        map.removeLayer(circle); // Remove circle when the popup is closed
      });

      let hoverTimeout;
      let closeTimeout;
      let hoverPopup;  // Keep a reference to the popup
      
      // Show a quote or message when the mouse hovers over the marker
      marker.on('mouseover', function() {
        clearTimeout(closeTimeout);
      
        hoverTimeout = setTimeout(function() {
          var hoverMessage = `“${poi.name}”`;
      
          // Define the popup's offset (move it 20px above the marker)
          var popupOffset = [0, -20];  // [horizontal offset, vertical offset]
      
          // Show the message as a popup, with 'closeButton' and 'closeOnClick' options disabled
          hoverPopup = L.popup({ 
            className: 'hover-popup', 
            closeButton: false,  // Disable the close button
            closeOnClick: false, // Disable closing on map click
            offset: popupOffset   // Apply the offset to position the popup above the marker
          })
            .setLatLng([poi.latitude, poi.longitude])
            .setContent(hoverMessage)
            .openOn(map);
        }, 100); // Delay before showing the popup
      });
      
      // Remove the hover quote when the mouse leaves the marker
      marker.on('mouseout', function() {
        clearTimeout(hoverTimeout);
      
        closeTimeout = setTimeout(function() {
          if (hoverPopup) {
            hoverPopup.close(); // Close the popup
            hoverPopup = null;
          }
        }, 500); // Delay before closing the popup
      });

    });
  })
  .catch((error) => console.error("Error fetching data:", error));

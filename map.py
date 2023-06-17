import folium, pandas

def create(database):
    data = pandas.read_csv(database)

    # Filter out entries without latitude or longitude
    filtered_data = data.dropna(subset=['latitude', 'longitude'])

    # Create a Folium map centered at the first POI
    map = folium.Map(location=[filtered_data.iloc[0]['latitude'], filtered_data.iloc[0]['longitude']], zoom_start=12)

    # Iterate over each filtered POI and add a marker to the map
    for index, row in filtered_data.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"<strong>{row['ESSID']}</strong><br>{row['password']}"
        ).add_to(map)

    # Save the map as an HTML file
    map.save('map.html')
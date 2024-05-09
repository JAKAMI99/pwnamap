import sqlite3
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import requests
import json
import os
from geojson import FeatureCollection, Feature, LineString


# Connect to SQLite
def get_db_connection():
    try:
        print("Attempting to connect to the SQLite database...")
        conn = sqlite3.connect("app/data/pwnamap.db")
        conn.row_factory = sqlite3.Row
        print("Connected to the database successfully.")
        return conn
    except Exception as e:
        print(f"Error connecting to the SQLite database: {str(e)}")
        return None


# Retrieve data from SQLite with a limit
def get_data(limit=300):
    conn = get_db_connection()
    if conn:
        query = f"SELECT latitude, longitude FROM wigle LIMIT {limit}"
        df = pd.read_sql_query(query, conn)
        conn.close()  # Don't forget to close the connection
        return df
    else:
        return pd.DataFrame()  # Return empty DataFrame if connection fails


# Clustering with DBSCAN (200 meters)
def cluster_points(data, eps=0.2, min_samples=1):
    km_per_degree = 110.574  # Conversion factor for degrees to kilometers
    eps_in_degrees = eps / km_per_degree  # 200 meters in degrees
    dbscan = DBSCAN(eps=eps_in_degrees, min_samples=min_samples, metric="euclidean")
    data["cluster"] = dbscan.fit_predict(data[["latitude", "longitude"]].values)
    return data


# Get the centroids of each cluster
def get_centroids(data):
    grouped = data.groupby("cluster").agg({
        "latitude": "mean",
        "longitude": "mean",
    })
    return grouped.reset_index()


# Fetch GeoJSON data from Overpass API
def fetch_osm_geojson(lat, lon, radius_m=200):
    query = f"""
    [out:json];
    (
      way(around:{radius_m},{lat},{lon})["highway"];
    );
    out geom;
    """
    url = "https://overpass.kumi.systems/api/interpreter"
    response = requests.post(url, data=query)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch OSM data: {response.status_code}")
        return None


# Compile GeoJSON data into a single object
def compile_geojson(data):
    features = []
    for feature_data in data:
        if feature_data is not None:
            for element in feature_data["elements"]:
                if "geometry" in element:
                    geometry = [
                        (coord["lon"], coord["lat"])
                        for coord in element["geometry"]
                    ]
                    features.append(
                        Feature(
                            geometry=LineString(geometry),
                            properties={"highway": element["tags"]["highway"]},
                        )
                    )
    return FeatureCollection(features)


# Save GeoJSON to a specified path
def save_geojson(geojson, geojson_path):
    # Ensure the base path exists
    directory = os.path.dirname(geojson_path)
    if not os.path.exists(directory):
        os.makedirs(directory)  # Create the directory if it doesn't exist

    try:
        with open(geojson_path, "w") as f:
            json.dump(geojson, f)
        print(f"GeoJSON file saved to {geojson_path}")
    except Exception as e:
        print(f"Error saving GeoJSON: {str(e)}")


# Generate GeoJSON and save it to a file
def main():
    base_path = "app/data/wardrive"  # Use relative path
    geojson_filename = "wardrive_overlay.json"
    geojson_path = os.path.join(base_path, geojson_filename)

    # Get data from SQLite (first 1000 data points for development)
    data = get_data(limit=1000)
    
    if not data.empty:
        clustered_data = cluster_points(data, eps=0.2)  # 200 meters
        centroids = get_centroids(clustered_data)
        
        osm_data = [fetch_osm_geojson(row["latitude"], row["longitude"], radius_m=200)
                    for _, row in centroids.iterrows()]
        
        geojson = compile_geojson(osm_data)
        
        save_geojson(geojson, geojson_path)  # Save GeoJSON to specified path
    else:
        print("No data found in SQLite.")


# Run the script
if __name__ == "__main__":
    main()

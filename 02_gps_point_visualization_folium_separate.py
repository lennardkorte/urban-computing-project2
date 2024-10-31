import folium
import pandas as pd
import ast
import os

# Load data
df = pd.read_csv('./data/train-1500.csv')

# Identify and store first 15 TRIP_IDs based on the earliest TIMESTAMP
selected_trip_ids = df.groupby("TRIP_ID").first().sort_values("TIMESTAMP").head(100).index

# Filter the data for these TRIP_IDs
trip_data = df[df['TRIP_ID'].isin(selected_trip_ids)]

# Extract coordinates and trip ids
trip_coords = [(trip_id, ast.literal_eval(polyline)) for trip_id, polyline in zip(trip_data['TRIP_ID'], trip_data['POLYLINE'].values)]
colors = ['blue', 'green', 'red', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']

# Generate a separate map for each trip
for idx, (trip_id, coords) in enumerate(trip_coords):
    # Bounding box for map view specific to each trip
    lons, lats = zip(*coords)
    margin = 0.005
    lon_min, lon_max = min(lons) - margin, max(lons) + margin
    lat_min, lat_max = min(lats) - margin, max(lats) + margin
    center_lat = (lat_min + lat_max) / 2
    center_lon = (lon_min + lon_max) / 2

    # Initialize map for each trip
    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=13, width=1500, height=1000)
    fmap.fit_bounds([[lat_min, lon_min], [lat_max, lon_max]])

    # Plot each trip with a unique color
    color = colors[idx % len(colors)]
    feature_group = folium.FeatureGroup(name=f'Trip {trip_id}')
    [folium.CircleMarker(location=(lat, lon), radius=3, color=color, fill=True, fill_opacity=1).add_to(feature_group) for lon, lat in coords]
    folium.PolyLine([(lat, lon) for lon, lat in coords], color=color, weight=2).add_to(feature_group)
    fmap.add_child(feature_group)

    # Save map for each trip with a unique filename
    os.makedirs('./data/separate_html/', exist_ok=True)
    fmap.save(f'./data/separate_html/porto_trip_{trip_id}.html')
    print(f"Map saved as ./data/separate_html/porto_trip_{trip_id}.html")

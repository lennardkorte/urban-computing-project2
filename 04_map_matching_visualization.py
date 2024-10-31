import os
import folium
import pandas as pd
import ast

# Load the original and matched data
df_original = pd.read_csv('./data/train-1500.csv')
df_matched = pd.read_csv('./data/matched_routines.csv')

# Define target trip IDs as integers for matching
target_trip_ids = [int("1372636854620000520"), int("1372638303620000112")]

# Toggle: set to True to iterate over first 15 trips, False to use target_trip_ids
use_first_15_trips = True

# Set the range of trip IDs based on the toggle
trip_ids = (
    df_original['TRIP_ID'].iloc[:15].tolist()  # Use first 15 trip IDs
    if use_first_15_trips 
    else target_trip_ids
)

# Iterate over each trip ID in the chosen list
for trip_id in trip_ids:
    # Locate the row index of the trip_id in the original data
    orig_index = df_original[df_original['TRIP_ID'] == trip_id].index
    if len(orig_index) == 0:
        print(f"Trip ID {trip_id} not found in the original data.")
        continue
    
    orig_index = orig_index[0]  # Get the row index for matching
    
    # Extract original coordinates from POLYLINE in train-1500.csv
    original_coords = ast.literal_eval(df_original.loc[orig_index, 'POLYLINE'])
    
    # Use the row index to find the matched row in matched_routines.csv
    matched_row = df_matched.iloc[orig_index]
    
    # Extract matched coordinates from 'mgeom' as WKT LINESTRING
    matched_coords = [
        tuple(map(float, coord.split()))
        for coord in matched_row['mapped_route_points'].replace("LINESTRING(", "").replace(")", "").split(",")
    ]

    # Set bounding box for consistent centering across maps
    all_points = original_coords + matched_coords
    lons, lats = zip(*all_points)
    margin = 0.005
    lon_min, lon_max = min(lons) - margin, max(lons) + margin
    lat_min, lat_max = min(lats) - margin, max(lats) + margin
    center_lat = (lat_min + lat_max) / 2
    center_lon = (lon_min + lon_max) / 2
    
    # Initialize map centered on route bounds
    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    fmap.fit_bounds([[lat_min, lon_min], [lat_max, lon_max]])
    
    # Feature group for layered control
    feature_group = folium.FeatureGroup(name=f'Trip {trip_id}')
    
    # Plot original route in blue with points
    folium.PolyLine([(lat, lon) for lon, lat in original_coords], color='blue', weight=2, opacity=0.7,
                    tooltip="Original Route").add_to(feature_group)
    for lon, lat in original_coords:
        folium.CircleMarker(location=(lat, lon), radius=3, color='blue', fill=True, fill_opacity=1).add_to(feature_group)
    
    # Offset matched route points to avoid overlap and plot in red with points
    matched_coords = [(lat + 0.001, lon + 0.001) for lat, lon in matched_coords]
    folium.PolyLine([(lat, lon) for lon, lat in matched_coords], color='red', weight=2, opacity=0.7,
                    tooltip="Matched Route").add_to(feature_group)
    for lon, lat in matched_coords:
        folium.CircleMarker(location=(lat, lon), radius=3, color='red', fill=True, fill_opacity=1).add_to(feature_group)
    
    # Add the feature group to the map
    fmap.add_child(feature_group)
    
    # Add layer control to toggle between routes
    fmap.add_child(folium.LayerControl())

    # Create output directory if it doesn't exist
    if not os.path.exists('./data/matched/'):
        os.makedirs('./data/matched/')

    # Save the map as an HTML file
    fmap.save(f'./data/matched/route_map_trip_matched_{trip_id}.html')
    print(f"Map for trip {trip_id} saved as route_map_trip_matched_{trip_id}.html")

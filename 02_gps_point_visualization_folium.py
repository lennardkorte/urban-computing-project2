import folium
import pandas as pd
import ast

# Load data
df = pd.read_csv('./data/train-1500.csv')

# Identify and store first 15 TRIP_IDs based on the earliest TIMESTAMP
selected_trip_ids = df.groupby("TRIP_ID").first().sort_values("TIMESTAMP").head(15).index

# Filter the data for these TRIP_IDs
trip_data = df[df['TRIP_ID'].isin(selected_trip_ids)]

# Extract coordinates
trip_coords = [ast.literal_eval(polyline) for polyline in trip_data['POLYLINE']]

# Bounding box for map view
all_points = [point for trip in trip_coords for point in trip]
lons, lats = zip(*all_points)

# Set map boundaries with margin (consistent with Code 2)
margin = 0.005
lon_min, lon_max = min(lons) - margin, max(lons) + margin
lat_min, lat_max = min(lats) - margin, max(lats) + margin

# Calculate center for consistent centering across both codes
center_lat = (lat_min + lat_max) / 2
center_lon = (lon_min + lon_max) / 2

# Initialize map and set bounds
fmap = folium.Map(location=[center_lat, center_lon], zoom_start=13, width=1500, height=1000)
fmap.fit_bounds([[lat_min, lon_min], [lat_max, lon_max]])
# Plot trips with unique colors
colors = ['blue', 'green', 'red', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']
for idx, coords in enumerate(trip_coords):
    color = colors[idx % len(colors)]
    feature_group = folium.FeatureGroup(name=f'Trip {idx + 1}')
    [folium.CircleMarker(location=(lat, lon), radius=3, color=color, fill=True, fill_opacity=1).add_to(feature_group) for lon, lat in coords]
    folium.PolyLine([(lat, lon) for lon, lat in coords], color=color, weight=2).add_to(feature_group)
    fmap.add_child(feature_group)

# Layer control and save map
fmap.add_child(folium.LayerControl())
fmap.save('./data/porto_trips_map_zoomed.html')
print("Map saved as ./data/porto_trips_map_zoomed.html")

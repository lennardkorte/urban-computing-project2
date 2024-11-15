import folium
import pandas as pd
import ast

# Load data
df = pd.read_csv('./data/task_6_results/improved_trip_data.csv')

# Function to plot trips based on specific TRIP_ID
def plot_trip(trip_id, color, map_center, map_bounds, filename):
    trip_data = df[df['TRIP_ID'] == trip_id]
    trip_coords = [ast.literal_eval(polyline) for polyline in trip_data['POLYLINE']]
    fmap = folium.Map(location=map_center, zoom_start=13, width=1500, height=1000)
    fmap.fit_bounds(map_bounds)

    feature_group = folium.FeatureGroup(name=f'Trip {trip_id}')
    for coords in trip_coords:
        [folium.CircleMarker(location=(lat, lon), radius=3, color=color, fill=True, fill_opacity=1).add_to(feature_group) for lon, lat in coords]
        folium.PolyLine([(lat, lon) for lon, lat in coords], color=color, weight=2).add_to(feature_group)
    fmap.add_child(feature_group)
    fmap.add_child(folium.LayerControl())
    fmap.save(filename)
    print(f"Map saved as {filename}")

# Identify the specific trips to plot
trip_ids_to_plot = [1372636854620000520, 1372638303620000112]

# Extract coordinates for bounding box calculation
all_points = []
for trip_id in trip_ids_to_plot:
    trip_data = df[df['TRIP_ID'] == trip_id]
    trip_coords = [ast.literal_eval(polyline) for polyline in trip_data['POLYLINE']]
    all_points.extend([point for trip in trip_coords for point in trip])

lons, lats = zip(*all_points)

# Set map boundaries with margin
margin = 0.005
lon_min, lon_max = min(lons) - margin, max(lons) + margin
lat_min, lat_max = min(lats) - margin, max(lats) + margin
map_center = [(lat_min + lat_max) / 2, (lon_min + lon_max) / 2]
map_bounds = [[lat_min, lon_min], [lat_max, lon_max]]

# Plot maps for individual trips
plot_trip('1372636854620000520', 'blue', map_center, map_bounds, './data/task_6_results/trip_1372636854620000520_.html')
plot_trip('1372638303620000112', 'red', map_center, map_bounds, './data/task_6_results/trip_1372638303620000112_.html')

# Create a combined map with both trips
combined_map = folium.Map(location=map_center, zoom_start=13, width=1500, height=1000)
combined_map.fit_bounds(map_bounds)

for trip_id, color in zip(trip_ids_to_plot, ['blue', 'red']):
    trip_data = df[df['TRIP_ID'] == trip_id]
    trip_coords = [ast.literal_eval(polyline) for polyline in trip_data['POLYLINE']]
    feature_group = folium.FeatureGroup(name=f'Trip {trip_id}')
    for coords in trip_coords:
        [folium.CircleMarker(location=(lat, lon), radius=3, color=color, fill=True, fill_opacity=1).add_to(feature_group) for lon, lat in coords]
        folium.PolyLine([(lat, lon) for lon, lat in coords], color=color, weight=2).add_to(feature_group)
    combined_map.add_child(feature_group)

combined_map.add_child(folium.LayerControl())
combined_map.save('./data/task_6_results/combined_trips_map.html')
print("Combined map saved as ./data/task_6_results/combined_trips_map.html")

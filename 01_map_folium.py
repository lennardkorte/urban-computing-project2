import folium

# Define the approximate central location of Porto
center_lat, center_lon = 41.1579, -8.6291  # Porto's geographical center

# Initialize map with fixed center on Porto and set a city-wide zoom level
fmap = folium.Map(location=[center_lat, center_lon], zoom_start=12, width=1500, height=1000)

# Save the map without points or trips
fmap.save('./data/porto_map_without_points_full_folium.html')
print("Map saved as ./data/porto_map_without_points_full_folium.html")

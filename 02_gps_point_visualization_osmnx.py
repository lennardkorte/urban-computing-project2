import osmnx as ox
import matplotlib.pyplot as plt
import ast
import random
import pandas as pd

# Load map and data
G = ox.graph_from_place("Porto, Portugal", network_type="drive", which_result=2)
df = pd.read_csv("./data/train-1500.csv")

# Select and process the first 15 trips
trip_data = df[df["TRIP_ID"].isin(df.groupby("TRIP_ID").first().sort_values("TIMESTAMP").head(15).index)]
all_points = [point for polyline in trip_data["POLYLINE"] for point in ast.literal_eval(polyline)]
lons, lats = zip(*all_points)

# Set map boundaries with margin
margin = 0.005
lon_min, lon_max = min(lons) - margin, max(lons) + margin
lat_min, lat_max = min(lats) - margin, max(lats) + margin

# Calculate center for consistent centering across both codes
center_lat = (lat_min + lat_max) / 2
center_lon = (lon_min + lon_max) / 2

# Plot map and trips
fig, ax = ox.plot_graph(G, show=False, close=False, figsize=(10, 10), bgcolor="white",
                        node_size=0, edge_color="gray", edge_linewidth=0.5)
ax.set_xlim(lon_min, lon_max)
ax.set_ylim(lat_min, lat_max)

# Plot GPS points for each trip with random colors
for _, group in trip_data.groupby("TRIP_ID"):
    points = [ast.literal_eval(row["POLYLINE"]) for _, row in group.iterrows()]
    for path in points:
        lons, lats = zip(*path)
        ax.plot(lons, lats, marker="o", markersize=2, color=[random.random() for _ in range(3)], linewidth=1.5)

# Customize and save plot
plt.title("First 15 Trips in Porto")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True)
plt.savefig("./data/first_15_trips_in_porto_zoomed.png", dpi=300, bbox_inches="tight")
plt.close(fig)

plt.title(f"First 15 Trips in Porto\nCenter: ({center_lat:.4f}, {center_lon:.4f})")
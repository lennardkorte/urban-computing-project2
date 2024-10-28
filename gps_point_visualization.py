import osmnx as ox
import matplotlib.pyplot as plt
import ast
import random
import pandas as pd

# Load the map of Porto, Portugal
place = "Porto, Portugal"
G = ox.graph_from_place(place, network_type="drive", which_result=2)

# Load the first 15 trips from the dataset
data_file = "./data/train-1500.csv"
df = pd.read_csv(data_file)

# Select the first 15 trips (unique TRIP_IDs)
first_15_trips = df.groupby("TRIP_ID").first().sort_values("TIMESTAMP").head(15).index
trip_data = df[df["TRIP_ID"].isin(first_15_trips)]

# Extract all GPS points from the first 15 trips to determine the bounding box
all_points = []
for polyline in trip_data["POLYLINE"]:
    points = ast.literal_eval(polyline)
    all_points.extend(points)
lons, lats = zip(*all_points)

# Determine map boundaries with a small margin
margin = 0.005  # Set a margin for zoom
lon_min, lon_max = min(lons) - margin, max(lons) + margin
lat_min, lat_max = min(lats) - margin, max(lats) + margin

# Set up the plot with the specified bounding box
fig, ax = ox.plot_graph(
    G,
    show=False,
    close=False,
    bgcolor="white",
    node_size=0,
    edge_color="gray",
    edge_linewidth=0.5,
    bbox=(lat_min, lat_max, lon_min, lon_max),
)

# Plot the GPS points for each trip
for trip_id, group in trip_data.groupby("TRIP_ID"):
    color = [random.random(), random.random(), random.random()]  # Random color for each trip
    for _, row in group.iterrows():
        # Extract GPS points (converting string representation to list of tuples)
        points = ast.literal_eval(row["POLYLINE"])
        lons, lats = zip(*points)
        ax.plot(lons, lats, marker="o", markersize=2, color=color, linewidth=1.5)

# Set title and labels
plt.title("First 15 Trips in Porto")
plt.xlabel("Longitude")
plt.ylabel("Latitude")

# Save the plot as a file
output_file = "./data/first_15_trips_in_porto_zoomed.png"
plt.savefig(output_file, dpi=300, bbox_inches="tight")
plt.close(fig)  # Close the plot to free memory

print(f"Plot saved as {output_file}")

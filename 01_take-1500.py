import csv
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Input and output file paths
input_file = './data/train.csv'
output_file = './data/train-1500.csv'
output_graph_file = './data/points_distribution.png'

# Dictionary to store trip data
trips = {}
trip_ids_in_order = []
taxi_ids_before = set()

# Step 1: Read the input file and store trip data
with open(input_file, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        trip_id = row['TRIP_ID']
        timestamp = int(row['TIMESTAMP'])
        taxi_id = row['TAXI_ID']
        taxi_ids_before.add(taxi_id)

        # If trip is already in trips dictionary, append the entry
        if trip_id in trips:
            trips[trip_id].append(row)
        else:
            # Add a new trip with a list containing the current entry
            trips[trip_id] = [row]
            trip_ids_in_order.append((trip_id, timestamp))

# Step 2: Sort trips by timestamp and select the first 1500 unique trips
# trip_ids_in_order.sort(key=lambda x: x[1])  # Sort by timestamp
selected_trip_ids = {trip_id for trip_id, _ in trip_ids_in_order[:1500]}

# Statistics to gather
single_point_polylines = 0
max_points = 0
total_points = 0
valid_linestrings = 0
points_per_trip = []
taxi_ids_after = set()

# Helper function to filter duplicates in a polyline
def filter_duplicate_points(polyline):
    if len(polyline) < 2:
        return polyline
    filtered_polyline = [polyline[0]]
    for point in polyline[1:]:
        if point != filtered_polyline[-1]:  # Add only if different from last added point
            filtered_polyline.append(point)
    return filtered_polyline

# Step 3: Write the selected trips to the output file and gather statistics
with open(output_file, 'w', newline='') as csvfile:
    fieldnames = ['TRIP_ID', 'CALL_TYPE', 'ORIGIN_CALL', 'ORIGIN_STAND', 'TAXI_ID', 
                  'TIMESTAMP', 'DAY_TYPE', 'MISSING_DATA', 'POLYLINE']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    # Write each selected trip with all its entries, excluding single-point trips
    for trip_id in selected_trip_ids:
        for row in trips[trip_id]:
            polyline = eval(row['POLYLINE'])  # Convert POLYLINE from string to list
            polyline = filter_duplicate_points(polyline)  # Remove consecutive duplicates
            num_points = len(polyline)
            
            # Exclude trips with only one point or empty polylines
            if num_points <= 1:
                single_point_polylines += 1
                continue

            # Write the row to the file
            row['POLYLINE'] = str(polyline)  # Convert back to string for writing
            writer.writerow(row)

            # Track statistics
            valid_linestrings += 1
            total_points += num_points
            points_per_trip.append(num_points)
            max_points = max(max_points, num_points)
            taxi_ids_after.add(row['TAXI_ID'])

# Calculate additional statistics
average_points = total_points / valid_linestrings if valid_linestrings > 0 else 0
std_dev_points = np.std(points_per_trip) if valid_linestrings > 0 else 0

# Plot the distribution of the number of points per trip and save it to a file
plt.figure(figsize=(10, 6))
plt.hist(points_per_trip, bins=50, edgecolor='black', log=True)  # Log scale for better visibility
plt.xlabel('Number of Points per Trip', fontsize=25)
plt.ylabel('Frequency (Log Scale)', fontsize=25)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)

plt.tight_layout()  # Adjust layout to fit labels within plot borders
plt.savefig(output_graph_file)
plt.close()

# Display results
print({
    "Number of Trips Before Subsetting": len(trip_ids_in_order),
    "Number of Unique Taxi IDs Before Subsetting": len(taxi_ids_before),
    "Number of Trips After Subsetting": len(selected_trip_ids),
    "Number of Unique Taxi IDs After Subsetting": len(taxi_ids_after),
    "Single Point Trips Removed": single_point_polylines,
    "Trip with Most Points": max_points,
    "Total Number of Points": total_points,
    "Total Number of Valid Trips": valid_linestrings,
    "Average Number of Points": average_points,
    "Standard Deviation of Points": std_dev_points
})

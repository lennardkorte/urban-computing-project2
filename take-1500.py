import csv
from datetime import datetime

# Input and output file paths
input_file = './data/train.csv'
output_file = './data/train-1500.csv'

# Dictionary to store trip data
trips = {}
trip_ids_in_order = []

# Step 1: Read the input file and store trip data
with open(input_file, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        trip_id = row['TRIP_ID']
        timestamp = int(row['TIMESTAMP'])

        # If trip is already in trips dictionary, append the entry
        if trip_id in trips:
            trips[trip_id].append(row)
        else:
            # Add a new trip with a list containing the current entry
            trips[trip_id] = [row]
            trip_ids_in_order.append((trip_id, timestamp))

# Step 2: Sort trips by timestamp and select the first 1500 unique trips
trip_ids_in_order.sort(key=lambda x: x[1])  # Sort by timestamp
selected_trip_ids = {trip_id for trip_id, _ in trip_ids_in_order[:1500]}

# Step 3: Write the selected trips to the output file
with open(output_file, 'w', newline='') as csvfile:
    fieldnames = ['TRIP_ID', 'CALL_TYPE', 'ORIGIN_CALL', 'ORIGIN_STAND', 'TAXI_ID', 
                  'TIMESTAMP', 'DAY_TYPE', 'MISSING_DATA', 'POLYLINE']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    # Write each selected trip with all its entries
    for trip_id in selected_trip_ids:
        for row in trips[trip_id]:
            writer.writerow(row)

print(f"Extracted data for the first 1500 trips by timestamp into {output_file}")

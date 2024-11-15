import os
import matplotlib.pyplot as plt
import pandas as pd
import math
import ast

# Create up output folder
os.makedirs('./data/task_6_results', exist_ok=True)

# Load and filter data
df = pd.read_csv('./data/train-1500.csv')
trip_data = df[df['TRIP_ID'].isin(df["TRIP_ID"].unique())]
trip_data['POLYLINE'] = trip_data['POLYLINE'].apply(ast.literal_eval)

# Calculate consecutive distances between GPS points
consecutive_dis_before = [
    math.sqrt((polyline[i][0] - polyline[i + 1][0]) ** 2 + (polyline[i][1] - polyline[i + 1][1]) ** 2) * 100
    for polyline in trip_data['POLYLINE'] if len(polyline) > 1
    for i in range(len(polyline) - 1)
]

# Plot histogram before applying the algorithm
plt.figure(figsize=(10, 6))
plt.hist(consecutive_dis_before, bins=50, color='blue', edgecolor='black', range=(0, 2), log=True)
plt.xlabel('Euclidean Distance (units)', fontsize=15)
plt.ylabel('Frequency (Log Scale)', fontsize=15)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.savefig("./data/task_6_results/consecutive_distances_histogram_before.png")
plt.close()

#Remove outliers from trip data
threshold_min, threshold_max, threshold_step = 0.005, 0.1, 0.005
threshold_noise = 0.0002
for index, row in trip_data.iterrows():
    polyline = row['POLYLINE']
    if len(polyline) < 2:
        continue
    modified_points = [polyline[0]]
    last_point, threshold = polyline[0], threshold_min
    for next_point in polyline[1:]:
        distance = math.sqrt((last_point[0] - next_point[0])**2 + (last_point[1] - next_point[1])**2)
        if distance < threshold and distance > threshold_noise:
            modified_points.append(next_point)
            last_point, threshold = next_point, threshold_min
        else:
            threshold = min(threshold + threshold_step, threshold_max)
    trip_data.at[index, 'POLYLINE'] = modified_points

# Calculate consecutive distances after applying the algorithm
consecutive_dis_after = [
    math.sqrt((polyline[i][0] - polyline[i + 1][0]) ** 2 + (polyline[i][1] - polyline[i + 1][1]) ** 2) * 100
    for polyline in trip_data['POLYLINE'] if len(polyline) > 1
    for i in range(len(polyline) - 1)
]

# Plot histogram after applying the algorithm
plt.figure(figsize=(10, 6))
plt.hist(consecutive_dis_after, bins=50, color='green', edgecolor='black', range=(0, 2), log=True)
plt.xlabel('Euclidean Distance (units)', fontsize=15)
plt.ylabel('Frequency (Log Scale)', fontsize=15)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.savefig("./data/task_6_results/consecutive_distances_histogram_after.png")
plt.close()

# Save the improved data
trip_data.to_csv("./data/task_6_results/improved_trip_data.csv", index=False)

print("Processing complete. Results saved in:", './data/task_6_results')

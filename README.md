# Instructions

## Task 1
### Third Party Libraries Required
- osmnx
- folium
- matplotlib
- shapely
- selenium
- numpy

### Files Required
- `data/train.csv`: This file should be placed into the `data` subfolder prior to running any script.

### Outputs
- `porto/edges.shp`
- `porto/nodes.shp`
- `data/train-1500.csv`
- `data/points_distribution.png`
- `data/porto_map_without_points_full_folium.html`
- `data/porto_map_without_points_full_osmnx.png`
- `data/porto_map_without_points_full_folium.png`

### Scripts to run
1. 01_download_network.ipynb
2. 01_map_folium.py
3. 01_map_folium_capture.py
4. 01_map_osmax.py
5. 01_take-1500.py

## Task 2
### Third Party Libraries Required
- pandas
- selenium
- matplotlib
- osmnx
-
### Files Required
- `data/train-1500.csv`  
### Outputs
- `data/first_15_trips_in_porto_zoomed.png`
- `data/porto_trips_map_zoomed.html`
- `data/porto_trips_map_zoomed.png`
- `data/separate_html/porto_trip_{trip_id}.html`
- `data/trip_screenshots/porto_trip_{trip_id}.png`

### Scripts to run
1. 02_gps_point_visualization_osmnx.py
2. 02_gps_point_visualization_folium.py
3. 02_gps_point_visualization_folium_capture.py
4. 02_gps_point_visualization_folium_separate.py
5. 02_gps_point_visualization_folium_capture_separate.py

## Task 3
### Third Party Programs
- Docker
### Third Party Libraries Required
- fmm

### Files Required
- `Dockerfile`
- `data/train-1500.csv`
- `porto/edges.shp`

### Outputs
- `data/matched.csv`
- `data/ubodt.txt`

### Scripts to run
1. 03_run.sh

## Task 4
### Third Party Libraries Required

### Files Required
- `data/matched.csv`

### Outputs
- `outputs/task4.png`

### Scripts to run
1. 04_fmm_visualization.py

## Task 5
### Third Party Libraries Required
- geopandas
- pillow
- pandas
- numpy
- matplotlib

### Files Required
- `data/train-1500.csv`
- `data/matched.csv`
- `porto/edges.shp`
  
### Outputs
**Misc**
- `data/edges_eid_to_osmid.csv`

**Visualizations**
- `outputs/task_5_1_all.png`
- `outputs/task_5_1_{rank}.png`
- `outputs/task_5_2_all.png`
- `outputs/task_5_2_{rank}.png`
- `outputs/task_5_overall.png`: 

**Top 10**
- `outputs/task_5_1_top10.csv`
- `outputs/task_5_2_top10.csv`

### Scripts to run
1. 05_eid_to_osmid_mappings.ipynb
2. 05_route_analysis.py

## Task 6
### Third Party Libraries Required
- folium
- selenium
- pandas
- matplotlib

### Files Required
- `data/train-1500.csv` 
### Outputs
- `data/task_6_results/{filename}`

### Scripts to run
1. 06_mm_improvement.py
2. 06_mm_improvement_visualize.py
3. 06_mm_improvement_visualize_capture.py
4. 06_mm_improvement_visualize_singles.py1.

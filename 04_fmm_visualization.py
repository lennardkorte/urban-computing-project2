import io
from PIL import Image
import pandas as pd
import geopandas as gpd
import shapely
from pyproj import CRS
import folium
import branca.colormap as cm

MATCH_RESULTS = './data/matched.csv'
crs = CRS("EPSG:4326")

def obtain_linestring(x):
    try:
        line = shapely.wkt.loads(x)
    except:
        line = None
    return line

def get_coords(geom):
    return list((y, x) for x, y in geom.coords)

df = pd.read_csv(MATCH_RESULTS)
df = df[['id', 'match_geom']]
df['geometry'] = df['match_geom'].apply(obtain_linestring)

gdf = gpd.GeoDataFrame(df, crs=crs)
gdf = gdf.loc[gdf['geometry'] != None, ['id','geometry']]
gdf['lcoord'] = gdf['geometry'].apply(get_coords)

fmm_coords = gdf.loc[:5, 'lcoord'].values
trip_coords = []
for trip in fmm_coords:
    formatted = [[coord[1], coord[0]] for coord in trip]
    trip_coords.append(formatted)

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
colormap = cm.linear.Set1_06.to_step(15).scale(0, 15)


for idx, coords in enumerate(trip_coords):
    color = colormap(idx)
    feature_group = folium.FeatureGroup(name=f'Trip {idx + 1}', tooltip=f"Line {idx+1}")
    [folium.CircleMarker(location=(lat, lon), radius=3, color=color, fill=True, fill_opacity=1).add_to(feature_group) for lon, lat in coords]
    folium.PolyLine([(lat, lon) for lon, lat in coords], color=color, weight=2).add_to(feature_group)
    fmap.add_child(feature_group, )

# Layer control and save map
fmap.add_child(folium.LayerControl())
img_data = fmap._to_png(5)
img = Image.open(io.BytesIO(img_data))
img.save('outputs/task4.png')
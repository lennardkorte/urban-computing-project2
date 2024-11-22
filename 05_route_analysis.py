import os
import re
import heapq
import requests 

import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt

from io import BytesIO
from PIL import Image
from collections import defaultdict

OVERPASS_URL = "http://overpass-api.de/api/interpreter"
USER_AGENT = "AI6128 Project"
TILE_CACHE = {}
WAY_CACHE = {}
print_for_latex = False
K = 10

def linestring_2_locations(x):
    x = re.findall('-?\d+[.]\d+', x)
    if len(x) == 0:
        return np.zeros((0,2))
    x = list(map(float, x))
    x = np.array(x).reshape((-1,2))
    
    return x

def s2l(x, type):
    if type == int:
        x = re.findall('\d+', x)
    else:
        x = re.findall('-?\d+[.]\d+', x)
    x = list(map(type, x))
    x = np.array(x)
    
    return x

def to_int(x):
    return s2l(x, int)

def to_float(x):
    return s2l(x, float)

def merge_bounding_boxes(box1, box2):
    min_x1, min_y1, max_x1, max_y1 = box1
    min_x2, min_y2, max_x2, max_y2 = box2
    
    return np.min([min_x1,min_x2]), np.min([min_y1, min_y2]), np.max([max_x1, max_x2]), np.max([max_y1, max_y2])

def lat_lon_padding(min_lon, min_lat, max_lon, max_lat, padding):
    avg_lat = np.radians((min_lat + max_lat) / 2)
    lat_padding = padding / 111320.0    
    lon_padding = padding / (111320.0 * np.cos(avg_lat))
    
    new_min_lat = min_lat - lat_padding
    new_max_lat = max_lat + lat_padding
    new_min_lon = min_lon - lon_padding
    new_max_lon = max_lon + lon_padding
    
    return new_min_lon, new_min_lat, new_max_lon, new_max_lat

def get_padded_bounding_box(lons, lats, padding):
    return lat_lon_padding(np.min(lons), np.min(lats), np.max(lons), np.max(lats), padding)

def pad_bounding_box(bbox, padding):
    min_lon, min_lat, max_lon, max_lat = bbox
    
    return get_padded_bounding_box([min_lon, max_lon], [min_lat, max_lat], padding)


def plot_bbox(bbox, ax, linewidth, color):
    min_lon, min_lat, max_lon, max_lat = bbox
    bbox_lon = [min_lon, min_lon, max_lon, max_lon, min_lon]
    bbox_lat = [max_lat, min_lat, min_lat, max_lat, max_lat]
    
    return ax.plot(bbox_lon, bbox_lat, linewidth=linewidth, color=color)

def plot_text_bbox(bbox, ax, text, color, fontsize):
    min_lon, min_lat, max_lon, max_lat = bbox
    
    return ax.text(max_lon, max_lat, text, color=color, fontsize=fontsize)

# https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
def deg2num(lat_deg, lon_deg, zoom):    
    lat_rad = np.radians(lat_deg)
    n = 1 << zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - np.arcsinh(np.tan(lat_rad)) / np.pi) / 2.0 * n)
    
    return xtile, ytile

def get_tile_range(bbox, zoom):
    min_lon, min_lat, max_lon, max_lat = bbox
    x1, y1 = deg2num(min_lat, min_lon, zoom)
    x2, y2 = deg2num(max_lat, max_lon, zoom)
    min_x = np.min([x1,x2])
    min_y = np.min([y1,y2])
    max_x = np.max([x1,x2])
    max_y = np.max([y1,y2])
    
    return min_x, min_y, max_x, max_y


def tile_to_bbox(x_tile, y_tile, zoom):
    n = 2 ** zoom
    lon_left = x_tile / n * 360.0 - 180.0
    lon_right = (x_tile + 1) / n * 360.0 - 180.0
    lat_top = np.degrees(np.arctan(np.sinh(np.pi * (1 - 2 * y_tile / n))))
    lat_bottom = np.degrees(np.arctan(np.sinh(np.pi * (1 - 2 * (y_tile + 1) / n))))
    
    return lon_left, lat_bottom, lon_right, lat_top

####### Begin definition of functions using requests #########

def get_ways(way_ids):
    required = []
    for wid in way_ids:
        if wid in WAY_CACHE:
            continue
        required.append(wid)

    if len(required) > 0:
        query = "[out:json];"
        for wid in required:
            query += f" way({wid}); out geom;"
    
        response = requests.post(OVERPASS_URL, data={"data": query})
        data = response.json()
        
        for way in data['elements']:
            WAY_CACHE[way['id']] = way

    ways = []
    for wid in way_ids:
        if wid in WAY_CACHE:
            way = WAY_CACHE[wid]
            ways.append(way)

    return ways

def get_tile(z,x,y):    
    tk = (z,x,y)
    if tk in TILE_CACHE:
        return TILE_CACHE[tk]

    
    url = f'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
    
    headers = {
        'User-Agent': USER_AGENT
    }
    
    response = requests.get(url, headers=headers)    
    img = Image.open(BytesIO(response.content))
    img = np.array(img.convert('RGB'))
    
    TILE_CACHE[tk] = img
    return img

####### End definition of functions using requests #########

def get_stitched_tiles(bbox, zoom):
    min_x, min_y, max_x, max_y = get_tile_range(bbox, zoom)
    tbbox1 = tile_to_bbox(min_x, min_y, zoom)
    tbbox2 = tile_to_bbox(max_x, max_y, zoom)
    min_lon, min_lat, max_lon, max_lat = merge_bounding_boxes(tbbox1, tbbox2)
    extent = [min_lon, max_lon, min_lat, max_lat]

    stitched = []
    for y in range(min_y, max_y+1):
        cols = []
        for x in range(min_x, max_x+1):
            tile = get_tile(zoom, x, y)
            cols.append(tile)
        row = np.hstack(cols)
        stitched.append(row)
    stitched = np.vstack(stitched)
    
    return stitched, extent

if __name__ == '__main__':
    print('Load data...')
    tdf = pd.read_csv('data/train-1500.csv')
    mdf = pd.read_csv('data/matched.csv')
    osm_edges = pd.read_csv('data/edges_eid_to_osmid.csv')
    os.makedirs('outputs', exist_ok=True)

    # get all unique edge ids
    all_eids_in_matches = []
    for path in mdf.match_path:
        all_eids_in_matches.extend(to_int(path))
    all_eids_in_matches = list(set(all_eids_in_matches))

    ### get all unique osm way ids in matches
    all_wids_in_matches = []
    for eid in all_eids_in_matches:
        all_wids_in_matches.extend(to_int(osm_edges.iloc[eid].osmid))
    all_wids_in_matches = list(set(all_wids_in_matches))
    
    print('Retrieve OSM way geometries...')
    all_ways_in_matches = get_ways(all_wids_in_matches)

    print('Computing approximate trajectory lengths of OSM ways...')
    ### calculate length of ways
    length_of_wids = defaultdict(lambda: 0)
    wid_to_way = {}
    for way in all_ways_in_matches:
        g = pd.DataFrame(way['geometry'])    
        dx = np.diff(g.lon)
        dy = np.diff(g.lat)
        segment_lengths = np.sqrt(dx**2 + dy**2)
        trajectory_length = np.sum(segment_lengths)
        length_of_wids[way['id']] = trajectory_length
        wid_to_way[way['id']] = way    
    
    ### analysis of trip frequency
    print('Analyzing Traversal Frequency...')
    number_of_trips = defaultdict(lambda: 0)
    for _, row in mdf.iterrows():
        eids = to_int(row.match_path)
        match_eids = to_int(row.match_edge_by_idx)
        trip_wids = []
        for i in range(len(match_eids)-1):
            a = match_eids[i]
            b = match_eids[i+1]
            wids = to_int(str(osm_edges.iloc[eids[a:b+1]].osmid.values))
            trip_wids.extend(wids)
        trip_wids = set(trip_wids)
        for wid in trip_wids:
            number_of_trips[wid] += 1

    #analysis of time spent
    print('Analyzing Time Spent...')
    time_spent = defaultdict(lambda: 0)    
    for _, row in mdf.iterrows():
        eids = to_int(row.match_path)
        match_eids = to_int(row.match_edge_by_idx)
        for i in range(len(match_eids)-1):
            a = match_eids[i]
            b = match_eids[i+1]
            wids = to_int(str(osm_edges.iloc[eids[a:b+1]].osmid.values))
            total_len = 0
            for wid in wids:
                l = length_of_wids[wid]
                total_len += l
            if total_len == 0:
                continue
            
            for wid in wids:
                l = length_of_wids[wid]
                time_spent[wid] += 15 * l/total_len

    print(f'Retrieving Top {K}...')
    num_of_trips_list = []
    avg_time_spent_list = []
    
    for wid in number_of_trips:
        num_of_trips_list.append((wid, number_of_trips[wid]))
    
    for wid in time_spent:
        if number_of_trips[wid] == 0:
            continue
        t = time_spent[wid]
        n = number_of_trips[wid]
        at = t/n
        if n < 0:
            continue
        avg_time_spent_list.append((wid, at, t, n))
    
    # get top K
    top_k_trips = heapq.nlargest(K, num_of_trips_list, key=lambda x: x[1])
    top_k_avg_time = heapq.nlargest(K, avg_time_spent_list, key=lambda x: x[1])

    # overall visualizations task 5.1
    print('Road Segments: Top-10 Most Traversed')
    top_10_entries = []
    padding = 100
    overall_bbox = None
    task_5_1_bboxes = []
    
    fig, ax = plt.subplots(1,1)
    for wid, n_trips in top_k_trips:
        g = pd.DataFrame(wid_to_way[wid]['geometry'])
        bbox = get_padded_bounding_box(g.lon, g.lat, padding)
        if overall_bbox is None:
            overall_bbox = bbox
        else:
            overall_bbox = merge_bounding_boxes(bbox, overall_bbox)
    
    task_5_1_bboxes.append(overall_bbox)
    stitched, extent = get_stitched_tiles(overall_bbox, 16)
    ax.imshow(stitched, extent=extent, alpha=.5)
        
    for i, (wid, n_trips) in enumerate(top_k_trips):
        way = wid_to_way[wid]
        g = pd.DataFrame(way['geometry'])
        if print_for_latex:
            print('%d & %d & %d \\ \hline' % (
                i+1,            
                way['id'], 
                n_trips
            ))
        else:
            print('%d. \t %-50s \t way id: %d \t n=%d' % (
                i+1,
                way['tags'].get('name', 'Unnamed'),
                way['id'], 
                n_trips
            ))
        top_10_entries.append({
            'rank': i+1,
            'name': way['tags'].get('name', 'Unnamed'),
            'id': way['id'],
            'n_trips': n_trips
        })
    
        segment_bbox = get_padded_bounding_box(g.lon, g.lat, 2)
        task_5_1_bboxes.append(segment_bbox)
        plot_bbox(segment_bbox, ax, 1, 'red')        
        plot_text_bbox(segment_bbox, ax, str(i+1), 'red', 12)
        ax.plot(g.lon, g.lat, '-', linewidth=1, label=f'{wid}', c='blue')
        
    pd.DataFrame(top_10_entries).to_csv(f'outputs/task_5_1_top{K}.csv', index=False)
    a,b,c,d = overall_bbox
    ax.set_xlim([a,c])
    ax.set_ylim([b,d])
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    current_width, current_height = fig.get_size_inches()
    fig.set_size_inches(current_width*2, current_height*2)
    fig.tight_layout()
    fig.savefig('outputs/task_5_1_all.png', bbox_inches='tight', pad_inches=0)
    plt.close(fig) 

    # overall visualizations task 5.2
    print('Road Segments: Top-10 Average Travelling Time')
    top_10_entries = []
    padding = 400
    overall_bbox = None
    task_5_2_bboxes = []
    fig, ax = plt.subplots(1,1)
    
    for wid, _,_,_ in top_k_avg_time:
        g = pd.DataFrame(wid_to_way[wid]['geometry'])
        bbox = get_padded_bounding_box(g.lon, g.lat, padding)
        if overall_bbox is None:
            overall_bbox = bbox
        else:
            overall_bbox = merge_bounding_boxes(bbox, overall_bbox)
    
    task_5_2_bboxes.append(overall_bbox)
    stitched, extent = get_stitched_tiles(overall_bbox, 14)
    ax.imshow(stitched, extent=extent, alpha=.5)
    
    for i,(wid, avg_time, total_time, n_trips) in enumerate(top_k_avg_time):
        way = wid_to_way[wid]
        g = pd.DataFrame(way['geometry'])
    
        if print_for_latex:
            print('%d & %d & %.2f & %d \\ \hline' % (
                i+1,
                way['id'], 
                avg_time,
                n_trips        
            ))
        else:
            print('%d. \t %-50s \t way id: %d \t %.2f sec \t n=%d' % (
                i+1,
                way['tags'].get('name', 'Unnamed'),
                way['id'], 
                avg_time,
                n_trips
            ))        
        top_10_entries.append({
            'rank': i+1,
            'name': way['tags'].get('name', 'Unnamed'),
            'id': way['id'],
            'avg_time': avg_time,
            'n_trips': n_trips
        })
            
        segment_bbox = get_padded_bounding_box(g.lon, g.lat, 2)
        task_5_2_bboxes.append(segment_bbox)  
        segment_bbox = get_padded_bounding_box(g.lon, g.lat, 100)
        plot_bbox(segment_bbox, ax, 1, 'red')    
        plot_text_bbox(segment_bbox, ax, str(i+1), 'red', 14)    
        ax.plot(g.lon, g.lat, '-', linewidth=1, label=f'{wid}', c = 'blue')
        
    pd.DataFrame(top_10_entries).to_csv(f'outputs/task_5_2_top{K}.csv', index=False)
    a,b,c,d = overall_bbox
    ax.set_xlim([a,c])
    ax.set_ylim([b,d])
    ax.axis('off')
    
    fig.tight_layout()    
    current_width, current_height = fig.get_size_inches()
    fig.set_size_inches(current_width*2, current_height*2)
    fig.savefig('outputs/task_5_2_all.png', bbox_inches='tight', pad_inches=0)
    plt.close(fig) 

    ### Figure for spatial distribution of top-10 for both task
    print('Generating combined figure...')
    bbox = merge_bounding_boxes(task_5_1_bboxes[0], task_5_2_bboxes[0])
    bbox_overall = pad_bounding_box(bbox, 100)
    fig, ax = plt.subplots(1,1)
    stitched, extent = get_stitched_tiles(bbox_overall, 13)
    h1,h2 = None, None
    ax.imshow(stitched, extent=extent, alpha=.5)
    for bbox in task_5_1_bboxes:
        h1, = plot_bbox(bbox, ax, 1, 'red')    
    for bbox in task_5_2_bboxes:
        h2, = plot_bbox(bbox, ax, 1, 'blue')   
    a,b,c,d = bbox_overall
    ax.set_xlim([a,c])
    ax.set_ylim([b,d])
    ax.axis('off')
        
    fig.tight_layout()
    current_width, current_height = fig.get_size_inches()
    fig.set_size_inches(current_width*2, current_height*2)
    ax.legend([h1,h2], ['Top-10 Most Traversed','Top-10 Average Travelling Time'], loc='upper right')
    fig.savefig('outputs/task_5_overall.png', bbox_inches='tight', pad_inches=0)
    plt.close(fig) 

    print('Generating individual figures...')
    # individual segment visualizations
    padding = 40
    for i, (wid, n_trips) in enumerate(top_k_trips):
        fig, ax = plt.subplots(1,1)
        g = pd.DataFrame(wid_to_way[wid]['geometry'])
        bbox = get_padded_bounding_box(g.lon, g.lat, padding)
        min_lon, min_lat, max_lon, max_lat = bbox
        stitched, extent = get_stitched_tiles(bbox, 18)
        ax.imshow(stitched, extent=extent)
        ax.plot(g.lon, g.lat, '-', c='red', linewidth=3)
        min_lon, min_lat, max_lon, max_lat = bbox
        
        ax.set_xlim([min_lon, max_lon])
        ax.set_ylim([min_lat, max_lat])    
        ax.axis('off')
        fig.savefig(f'outputs/task_5_1_{i+1}.png', bbox_inches='tight', pad_inches=0)
        plt.close(fig) 

    padding = 40
    for i, (wid, avg_time, total_time, n_trips) in enumerate(top_k_avg_time):
        fig, ax = plt.subplots(1,1)
        g = pd.DataFrame(wid_to_way[wid]['geometry'])
        bbox = get_padded_bounding_box(g.lon, g.lat, padding)
        min_lon, min_lat, max_lon, max_lat = bbox
        stitched, extent = get_stitched_tiles(bbox, 18)
        ax.imshow(stitched, extent=extent)
        ax.plot(g.lon, g.lat, '-', c='red', linewidth=3)
        min_lon, min_lat, max_lon, max_lat = bbox
        ax.set_xlim([min_lon, max_lon])
        ax.set_ylim([min_lat, max_lat])
        ax.axis('off')
        fig.savefig(f'outputs/task_5_2_{i+1}.png', bbox_inches='tight', pad_inches=0)
        plt.close(fig) 

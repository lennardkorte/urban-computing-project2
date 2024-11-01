import json
import requests
import pandas as pd
import numpy as np

# Define paths and parameters
input_file = "./data/train-1500.csv"
output_file = "./data/matched.csv"
trip_limit = 15  # Limit processing to first 15 trips
search_radius = 30
valhalla_base_url = 'http://localhost:8002'

def prep_df(df):
    df['trip_points'] = df.POLYLINE.apply(json.loads).apply(np.array)
    df['n_trip_points'] = df.trip_points.apply(lambda x: x.shape[0])
    df = df.sort_values(by='TRIP_ID')
    return df

def get_timed_trip_points(df):
    lon,lat = np.vstack(df.apply(lambda row: row.trip_points if row.n_trip_points else np.zeros((0,2)),axis=1).values).T
    times = np.concatenate(df.apply(lambda row: row.TIMESTAMP + np.arange(0, row.n_trip_points) * 15, axis=1).values)
    trip_ids = np.concatenate(df.apply(lambda row: np.repeat(row.TRIP_ID, row.n_trip_points),axis=1).values)
    times = pd.to_datetime(times, unit='s')
    
    req_df = pd.DataFrame()
    req_df['times'] = times
    req_df['lon'] = lon
    req_df['lat'] = lat
    req_df['TRIP_ID'] = trip_ids

    return req_df


def trace_route_request(ttpdf):
    url = valhalla_base_url + '/trace_route'
    headers = {'Content-type': 'application/json'}
    meili_head = '{"shape":'
    meili_tail = ',"search_radius": %d, "shape_match":"map_snap", "costing":"auto", "format":"osrm"}' % (search_radius)
    meili_shapes = ttpdf.to_json(orient='records')
    
    data = meili_head + meili_shapes + meili_tail
    response = requests.post(url, data=data, headers=headers)
    return response.json()

def main():
    df = pd.read_csv(input_file)
    df = prep_df(df)
    i = 0  
    rows = []
    n_trips = df.TRIP_ID.value_counts().index.shape[0] 
    print("Map matching: %d/%d trips from %s" % (trip_limit, n_trips, input_file))
    for tid, grp in df.groupby('TRIP_ID'):
        row = {}
        ttpdf = get_timed_trip_points(grp)
        row['gps'] = ttpdf[['lon','lat']].values.tolist()
        row['TRIP_ID'] = tid

        if ttpdf.shape[0] == 0:
            continue
        
        resp = trace_route_request(ttpdf)
        locations = [x['location'] for x in resp['tracepoints'] if x is not None]
        if len(locations) == 0:
            continue

        i += 1
        if i > trip_limit:
            break

        locations = str(locations)
        row['matched'] = locations
        rows.append(row)

    output = pd.DataFrame(rows)
    output.to_csv(output_file)
    print("Map matching: Completed, results saved to {}".format(output_file))

if __name__ == '__main__':
    main()

import os
import csv
from fmm import FastMapMatch, Network, NetworkGraph, UBODTGenAlgorithm, UBODT, FastMapMatchConfig

# Define paths and parameters
network_file = "./porto/edges.shp"
ubodt_file = "./data/ubodt.txt"
input_file = "./data/train-1500.csv"
output_file = "./data/matched_results_1500_updated.csv"
trip_limit = 1500  # Limit processing to first 15 trips

# Map matching parameters
search_radius = 0.05
k_neighbors = 10
gps_accuracy = 0.005
ubodt_distance_threshold = 0.02
regen_ubodt = False

# Load or generate the network
if not os.path.exists(network_file):
    print("Network file {} does not exist.".format(network_file))
else:
    network = Network(network_file, "fid", "u", "v")
    print("Loaded network with {} nodes and {} edges.".format(network.get_node_count(), network.get_edge_count()))
    graph = NetworkGraph(network)
    
    # Generate UBODT if missing or flagged for regeneration
    if not os.path.exists(ubodt_file) or regen_ubodt:
        print("Generating UBODT file.")
        ubodt_gen = UBODTGenAlgorithm(network, graph)
        ubodt_gen.generate_ubodt(ubodt_file, ubodt_distance_threshold, binary=False, use_omp=True)
    
    # Load UBODT file
    ubodt = UBODT.read_ubodt_csv(ubodt_file)
    
    print("Starting map matching process.")
    with open(input_file, "r") as csv_input, open(output_file, "w") as csv_output:
        print("Opened input and output files.")
        csv_reader = csv.reader(csv_input)
        csv_writer = csv.writer(csv_output)
        
        headers = next(csv_reader)
        trip_id_index = headers.index("TRIP_ID")
        polyline_index = headers.index("POLYLINE")
        
        # Write header for output
        csv_writer.writerow(["idx", 
                             "id",
                             "match_path",
                             "match_edge_by_pt",
                             "match_edge_by_idx",
                             "match_geom",
                             "edge_id",
                             "source",
                             "target",
                             "error",
                             "length",
                             "offset",
                             "spdist",
                             "ep",
                             "tp",
                             ])

        
        
        print("Processing rows for map matching.")
        for row_index, row in enumerate(csv_reader):
            if trip_limit is not None and row_index >= trip_limit:
                print("Limit of {} trips reached.".format(trip_limit))
                break
            try:
                trip_id = row[trip_id_index]
                trajectory = eval(row[polyline_index])
                
                # Convert trajectory to WKT format
                wkt_path = 'LINESTRING(' + ','.join([' '.join(map(str, point)) for point in trajectory]) + ')'
                
                # Initialize map-matching model and configuration
                map_matcher = FastMapMatch(network, graph, ubodt)
                map_matcher_config = FastMapMatchConfig(k_neighbors, search_radius, gps_accuracy)

                # Perform map matching
                print("Matching trip {}.".format(trip_id))
                match_result = map_matcher.match_wkt(wkt_path, map_matcher_config)
                print("Matched trip {}.".format(trip_id))

                # Write matched result
                csv_writer.writerow([row_index, 
                                    trip_id,
                                    match_result.cpath,
                                    match_result.opath,
                                    match_result.indices,
                                    match_result.mgeom.export_wkt(),
                                    match_result.pgeom.export_wkt(),
                                    [c.edge_id for c in match_result.candidates],
                                    [c.source for c in match_result.candidates],
                                    [c.target for c in match_result.candidates],
                                    [c.error for c in match_result.candidates],
                                    [c.length for c in match_result.candidates],
                                    [c.offset for c in match_result.candidates],
                                    [c.spdist for c in match_result.candidates],
                                    [c.ep for c in match_result.candidates],
                                    [c.tp for c in match_result.candidates],
                                    ])
                
            except Exception as e:
                print("Error processing row {}: {}".format(row_index, e))

    print("Map matching completed. Results saved to {}".format(output_file))

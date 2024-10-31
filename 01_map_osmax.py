import osmnx as ox
import matplotlib.pyplot as plt

# Load map for Porto
G = ox.graph_from_place("Porto, Portugal", network_type="drive", which_result=2)

# Plot map without points and without zooming in
fig, ax = ox.plot_graph(G, show=False, close=False, figsize=(10, 10), bgcolor="white",
                        node_size=0, edge_color="gray", edge_linewidth=0.5)

# Customize and save plot without points and without zoom
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True)
plt.savefig("./data/porto_map_without_points_full_osmnx.png", dpi=300, bbox_inches="tight")
plt.close(fig)

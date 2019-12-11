import pickle
import networkx as nx
import fiona


##############################################################################################

# read in
road_network = nx.read_gpickle('ca_roads_full.gpickle')


# example of how to access weights!!! for loop?
# list(G.edges)['edge #'][ 0='starting node' / 1='ending node ][0=lon / 1=lat]
lon_n =  list(G.edges)[1][0][0]
lat_n = list(G.edges)[1][0][1]

lon_m =  list(G.edges)[1][1][0]
lat_m =  list(G.edges)[1][1][1]

G.get_edge_data((lon_n, lat_n), (lon_m, lat_m))['weight']
# {'weight': 0.004747248992832023}
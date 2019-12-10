# playing with road networks to figure out out to turn shapefile into network graph, 
# on which to perform djikstra's algorithm
import pickle

from shapely.geometry import shape
from shapely.ops import unary_union
import networkx as nx
import fiona
# import itertools


# set data directory and define data sources
# DATA_DIR = "/Users/anayahall/Box/compostsiting/data"
roads_shapefile = "roads/tl_2019_06_prisecroads.shp"


# roads_G = 'data/ca_roads.gpickle'
# G = nx.read_gpickle(roads_G)


# combine the lines of the shapefile
# lines =[shape(line['geometry']) for line in fiona.open("data/tl_2019_06_prisecroads/tl_2019_06_prisecroads.shp")]
lines =[shape(feature['geometry']) for feature in fiona.open(roads_shapefile)]


# alt method?
# G = nx.Graph()
# for line in lines:
#    for seg_start, seg_end in zip(list(line.coords),list(line.coords)[1:]):
#     G.add_edge(seg_start, seg_end) 

print("starting union")

result = unary_union(lines) # crashes here! # might need to do something else with multigeometries

print("result object created - try to save... ")

# raise Exception("RESULTS DONE!")

# with open('data/lines_union.p', 'wb') as f:
# 	pickle.dump(result, f)

G = nx.Graph()
import itertools
for line in result:
   for seg_start, seg_end in zip(list(line.coords),list(line.coords)[1:]):
       G.add_edge(seg_start, seg_end)

# print("edges made")
# nx.write_gpickle(G, 'data/ca_roads_full.gpickle')

# Roads
# road_network = gpd.read_file(opj(DATA_DIR, 
#                                  roads_shapefile))  


## calculate where all the intersecting nodes 
# using intersections of linestrings
# -- then save so only need to do once

# # Node list
# NodeList_duplicates = np.empty((0,4), int)
# for i in range(len(road_network)):
#     if i % 1000 == 0:
#         print("STILL RUNNING: ", i)
#     # grab linestring
#     m = road_network.loc[i, 'geometry']
#     # loop through all other linestrings
#     for j in range(len(road_network)):
#         if j != i:
#             n = road_network.loc[j, 'geometry']
#             if m.intersection(n):
#     #             print('NODE FOUND of type:', m.intersection(n).type)
#                 if m.intersection(n).type == 'Point':
#     #                 print(i,j)
#                     (x,y) = m.intersection(n).x, m.intersection(n).y
#     #                 print(x,y)
#                     i_id = road_network.loc[i, 'LINEARID']
#                     j_id = road_network.loc[j, 'LINEARID']
#                     # set up node list : lineid, lineid, (coords)
#                     NodeList_duplicates = np.append(NodeList_duplicates, 
#                                                     np.array([[i_id, j_id, x, y]]), 
#                                                     axis = 0 )
# # save as only unique
# nodelist = np.unique(NodeList_duplicates, axis=0)

# # picke and save node list
# with open('nodelist.p', 'wb') as f:
#     pickle.dump(nodelist, f)     

# Load node list from intersection calculation
# with open('nodelist.p', 'rb') as f:
#     nodelist = pickle.load(f)

# node_lons = (nodelist[np.array([np.arange(len(nodelist))]), 2]).T
# node_lats = (nodelist[np.array([np.arange(len(nodelist))]), 3]).T
# # create shapely point series from nodes (to use to split linestrings below)
# node_pts =  [Point(x,y) for x, y in zip(node_lons, node_lats)]
    
#node_pts

# Now that I have created all the nodes, create all the edges 
# using the split tool in shapely

# create empty array
# edgelist = []
# loop through all lines in network
# for l in range(len(road_network)):
#     if l % 100 == 0:
#         print("STILL RUNNING: ", l)
#     # grab linestring
#     line = road_network.loc[l, 'geometry']
#     # check if linestring intersects (required for split)
#     for point in node_pts:
#         if point.intersection(line):
# #             print('YES')
#             splitted = split(line, point)
#             edgelist.append(splitted)

# # this takes about three hours so save it and re-load for next use
# with open('edgestrings.p', 'wb') as f:
#     pickle.dump(edgelist, f)
    
# with open('edgestrings.p', 'rb') as f:
#     edgelist = pickle.load(f)

# # CREATE ADJACENCY MATRIX
# L = np.zeros(((len(node_pts),(len(node_pts)))))
# D = np.full(((len(node_pts),(len(node_pts)))), np.inf)

# # walk it out walk it out!
# for i, geom in enumerate(edgelist):
# #     if i % 100 == 0:
# #         print("still running??? ", i)
#     print(i)
#     for g in geom:
#         line_lons, line_lats = g.xy
#         road_length = g.length
# #         print(line_lons[0], line_lats[0])
#         for n in range(len(node_pts)): ### index of node
# #             print(n)
# #             print(node_pts[n].x, node_pts[n].y)
#             if np.sum([line_lons[0], line_lats[0]] == [node_pts[n].x, node_pts[n].y]) == 1: 
#                 start_j = n
#             if np.sum([line_lons[-1], line_lats[-1]] == [node_pts[n].x, node_pts[n].y]) == 1:
#                 end_j = n
#         L[start_j, end_j] = 1 
#         L[end_j, start_j] = 1
#         D[start_j, end_j] = road_length
#         D[end_j, start_j] = road_length

# # import scipy.sparse
# L_sparse = scipy.sparse.csc_matrix(L)

# D_sparse = scipy.sparse.csc_matrix(D)

# # # if this works save it!!        
# with open('adjacency.p', 'wb') as f:
#     pickle.dump(L_sparse, f)
    
# # if this works save it!!        
# with open('distance.p', 'wb') as f:
#     pickle.dump(D_sparse, f)
# then open it later    
# with open('adjacency.p', 'rb') as f:
#     L = pickle.load(f)

# with open('distance.p', 'rb') as f:
#     D = pickle.load(f)






### NOTES:

# shapely & fiona issues when using unary_union
# https://github.com/Toblerity/Shapely/issues/553

# planar graph guide: basically, grab lines, create union, get segments of resulting lines and add them as 
# edges to a new graph
# https://gis.stackexchange.com/questions/213369/how-to-calculate-edge-length-in-networkx


# if issues with MULTIGEOMETRIES see here:
# https://gis.stackexchange.com/questions/239633/how-to-convert-a-shapefile-into-a-graph-in-which-use-dijkstra?noredirect=1&lq=1










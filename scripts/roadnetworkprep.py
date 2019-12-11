# playing with road networks to figure out out to turn shapefile into network graph, 
# on which to perform djikstra's algorithm

# NOTE: VERY SLOW!! run on server!!


import pickle
from shapely.geometry import shape
# from shapely.ops import unary_union
from shapely.ops import split
import networkx as nx
import fiona
import geopandas as gpd
import numpy as np

##############################################################################################

# # set data directory and define data sources
# # DATA_DIR = "/Users/anayahall/Box/compostsiting/data"
roads_shapefile = "roads/tl_2019_06_prisecroads.shp"

# # combine the lines of the shapefile
# # lines =[shape(line['geometry']) for line in fiona.open("data/tl_2019_06_prisecroads/tl_2019_06_prisecroads.shp")]
# lines =[shape(feature['geometry']) for feature in fiona.open(roads_shapefile)]


# print("starting union")

# result = unary_union(lines) # crashes here! # might need to do something else with multigeometries

# print("result object created - try to save... ")


# G = nx.Graph()
# import itertools
# for line in result:
#     weight = line.length
#     for seg_start, seg_end in zip(list(line.coords),list(line.coords)[1:]):
#        G.add_edge(seg_start, seg_end, weight = weight)

# # print("edges made")
# nx.write_gpickle(G, 'ca_roads_full.gpickle')

############################################################################################


### NOTES:

# shapely & fiona issues when using unary_union
# https://github.com/Toblerity/Shapely/issues/553

# planar graph guide: basically, grab lines, create union, get segments of resulting lines and add them as 
# edges to a new graph
# https://gis.stackexchange.com/questions/213369/how-to-calculate-edge-length-in-networkx


# if issues with MULTIGEOMETRIES see here:
# https://gis.stackexchange.com/questions/239633/how-to-convert-a-shapefile-into-a-graph-in-which-use-dijkstra?noredirect=1&lq=1




############################################################################################
# ALTERNATE ATTEMPT TO BUILD OUT ADJ MATRIX
#############################################################################################

# load roads

road_full = gpd.read_file(roads_shapefile)

# reduce size
road_full = road_full[road_full['RTTYP'] != 'S']
road_full = road_full[road_full['RTTYP'] != 'M']

print("LOADED AND REDUCED - START ANALYSIS with NODES")
# do analysis from here
road_network = road_full

road_network = road_network.reset_index(drop=True)

## calculate where all the intersecting nodes 
# using intersections of linestrings
# -- then save so only need to do once

# # Node list
NodeList_duplicates = np.empty((0,4), int)
# loop through all to find points
for i in range(len(road_network)):
    # print(i)
    if i % 100 == 0:
        print("NODES STILL RUNNING: ", i)
    # grab linestring
    m = road_network.loc[i, 'geometry']
    # loop through all other linestrings
    for j in range(len(road_network)):
        if j != i:
            n = road_network.loc[j, 'geometry']
            if m.intersection(n):
    #             print('NODE FOUND of type:', m.intersection(n).type)
                if m.intersection(n).type == 'Point':
    #                 print(i,j)
                    (x,y) = m.intersection(n).x, m.intersection(n).y
    #                 print(x,y)
                    i_id = road_network.loc[i, 'LINEARID']
                    j_id = road_network.loc[j, 'LINEARID']
                    # set up node list : lineid, lineid, (coords)
                    NodeList_duplicates = np.append(NodeList_duplicates, 
                                                    np.array([[i_id, j_id, x, y]]), 
                                                    axis = 0 )


# # save as only unique
nodelist = np.unique(NodeList_duplicates, axis=0)

# # picke and save node list
# with open('nodelist.p', 'wb') as f:
#     pickle.dump(nodelist, f)     

# Load node list from intersection calculation
# with open('nodelist.p', 'rb') as f:
#     nodelist = pickle.load(f)

node_lons = (nodelist[np.array([np.arange(len(nodelist))]), 2]).T
node_lats = (nodelist[np.array([np.arange(len(nodelist))]), 3]).T
# create shapely point series from nodes (to use to split linestrings below)
node_pts =  [Point(x,y) for x, y in zip(node_lons, node_lats)]
    
#node_pts

print("NODE LIST COMPLETE - NEXT IS EDGELIST")

# Now that I have created all the nodes, create all the edges 
# using the split tool in shapely

# create empty array
edgelist = []
# loop through all lines in network
for l in range(len(road_network)):
    if l % 100 == 0:
        print("EDGES STILL RUNNING: ", l)
    # grab linestring
    line = road_network.loc[l, 'geometry']
    # check if linestring intersects (required for split)
    for point in node_pts:
        if point.intersection(line):
#             print('YES')
            splitted = split(line, point)
            edgelist.append(splitted)

# # this takes about three hours so save it and re-load for next use
with open('edgestrings.p', 'wb') as f:
    pickle.dump(edgelist, f)
    
# with open('edgestrings.p', 'rb') as f:
#     edgelist = pickle.load(f)

print("EDGE LIST MADE - NEXT IS ADJACENCY and DISTANCE MATRICES")

# # CREATE ADJACENCY MATRIX
L = np.zeros(((len(node_pts),(len(node_pts)))))
D = np.full(((len(node_pts),(len(node_pts)))), np.inf)

# # walk it out walk it out!
for i, geom in enumerate(edgelist):
    if i == 1:
        print("WALK IT OUT!")
    for g in geom:
        line_lons, line_lats = g.xy
        road_length = g.length
#         print(line_lons[0], line_lats[0])
        for n in range(len(node_pts)): ### index of node
#             print(n)
#             print(node_pts[n].x, node_pts[n].y)
            if np.sum([line_lons[0], line_lats[0]] == [node_pts[n].x, node_pts[n].y]) == 1: 
                start_j = n
            if np.sum([line_lons[-1], line_lats[-1]] == [node_pts[n].x, node_pts[n].y]) == 1:
                end_j = n
        L[start_j, end_j] = 1 
        L[end_j, start_j] = 1
        D[start_j, end_j] = road_length
        D[end_j, start_j] = road_length

print("BIG MATRICES DONE!!!")

# # import scipy.sparse
# L_sparse = scipy.sparse.csc_matrix(L)

# D_sparse = scipy.sparse.csc_matrix(D)

# # # if this works save it!!        
with open('adjacency.p', 'wb') as f:
    pickle.dump(L, f)
    
# if this works save it!!        
with open('distance.p', 'wb') as f:
    pickle.dump(D, f)

# then open it later    
# with open('adjacency.p', 'rb') as f:
#     L = pickle.load(f)

# with open('distance.p', 'rb') as f:
#     D = pickle.load(f)


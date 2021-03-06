# PP275 Final Project
# Anaya Hall
# Nov. 28, 2019

# This project takes in 

# SEE roadnetworkprep.py for more detail on generating road network

##############################################################################################
# IMPORT PACKAGES AND SET DATA SOURCES
##############################################################################################

#import packages
import pickle
from os.path import join as opj
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, MultiPoint, Polygon, MultiPolygon
from shapely.ops import cascaded_union
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from shapely.ops import nearest_points


# import other scripts??
from support_functions import shortest_path

# set data directory # 

# LOCAL DATA DIR
# DATA_DIR = "/Users/anayahall/Box/compostsiting/data"

# SERVER DATA DIR
DATA_DIR = "data"

### Data used in this script:
# CALIFORNIA SHAPES
california_counties_shapefile = "CA_Counties/CA_Counties_TIGER2016.shp"
cal_tracts_shapefile = "tract/tl_2019_06_tract.shp"

# MSW, ROADS, FACILITIES
msw_shapefile = "msw_2020/msw_2020.shp"
#tracts_msw_shapefile = "tracts_msw/tracts_msw.shp"
roads_shapefile = "tl_2019_06_prisecroads/tl_2019_06_prisecroads.shp"
compost_facilities_shapefile = "clean_swis/clean_swis.shp" # note: PREVIOUSLY CLEANED!
rangelands_shapefile = "gl_bycounty/grazingland_county.shp"
cropland_shapefile = "Crop__Mapping_2014/Crop__Mapping_2014.shp"

# SOCIAL/ECONOMIC/POLITICAL
calenviroscreen_shapefile = "calenviroscreen/CESJune2018Update_SHP/CES3June2018Update_4326.shp"
oppzones_shapefile= "Opportunity Zones/8764oz.shp"
air_district_shapefile = "ca_air_district/CaAirDistrict.shp"

## USER-DEFINED PARAMETERS
buffer_km = 75 # //TODO COULD MAKE THIS A USER INPUT SOMEWHERE ELSE! 

print("DATA READY TO LOAD")

##############################################################################################
# LOAD DATA
##############################################################################################


##### California counties ##########
california = gpd.read_file(opj(DATA_DIR, 
        california_counties_shapefile))
# set to convention for california 4326 (so all in degrees!)
california = california.to_crs(epsg=4326)

# california census tracts (polygons)
cal_tracts = gpd.read_file(opj(DATA_DIR, 
                              cal_tracts_shapefile))

# # tract polygons waith attached msw 
# (FOR PLOTTING ONLY -- IGNORE FOR NOW)
# tracts_msw = gpd.read_file(opj(DATA_DIR,
#                               tracts_msw_shapefile))
# tracts_msw = tracts_msw[(tracts_msw['subtype'] == "MSWfd_wet_dryad_wetad") | (tracts_msw['subtype'] == "MSWgn_dry_dryad")]
# tracts_msw['subtype'].replace({'MSWfd_wet_dryad_wetad': 'MSW_food', 
#                         'MSWgn_dry_dryad': 'MSW_green'}, inplace = True)
###################################



##### Municipal Solid Waste (points) #####
msw = gpd.read_file(opj(DATA_DIR,
                  msw_shapefile))
# filter to just keep food and green waste (subject of regulations)
msw = msw[(msw['subtype'] == "MSWfd_wet_dryad_wetad") | (msw['subtype'] == "MSWgn_dry_dryad")]

# MSW DATA NOTES: 
# fog = Fats, Oils, Grease; lb = lumber; cd = cardboard; fd = food;
# pp = paper, gn = green; ot = Other ; suffix describes what the 
# waste is deemed suitable for

# rename categories to be more intuitive
msw['subtype'].replace({'MSWfd_wet_dryad_wetad': 'MSW_food', 
                        'MSWgn_dry_dryad': 'MSW_green'}, inplace = True)
# msw_sum =  msw.groupby(['County', 'subtype']).sum() # may combine???
msw_total = msw.groupby(['ID', 'County']).sum()

# ADJUST VALUES 
# I'll be using 100% of the GREEN waste, so leave as is
# for FOOD WASTE, take off 2.5%, 
# then of the remainer divert 62.5% of generation to compost
# (assume that 25% goes straight to compost, 75% goes to AD, which reduces volume of material by half, 
# before being composted)
# equivlant to 0.609375
# create new array of values
new_wt_values = msw[msw['subtype'] == 'MSW_food']['wt']*0.609375
# replace these in place!
msw.loc[msw['subtype'] == 'MSW_food', 'wt'] = new_wt_values
###################################



##### Roads #########################
road_network = gpd.read_file(opj(DATA_DIR, 
                                 roads_shapefile))
# BRING IN JUST FOR PLOTTING!
# not necessary --- bring these in as adjacency matrices later!!
###################################



##### Composting Facilities ##########
composters = gpd.read_file(opj(DATA_DIR,
                                compost_facilities_shapefile))
# change capacity metric to tons!
composters['cap_ton'] = composters['cap_m3']*0.58
########################################



##### LAND (END USE MARKETS) ###################
# RANGEALND
rangelands = gpd.read_file(opj(DATA_DIR,
                              rangelands_shapefile))
rangelands = rangelands.to_crs(epsg=4326) # make sure this is in the right projection
# identify centroid for use in node assignment
rangelands['centroid'] = rangelands['geometry'].centroid

rangelands['area_ha'] = rangelands['Shape_Area']/10000 # convert area in m2 to hectares
rangelands['capacity_tons'] = rangelands['area_ha'] * 36.83

# Read in cropland data
print("--reading in CROP MAP--")

# THIS TAKES A LONG TIME - JUST READ IN SMALLER FILE
# cropmap = gpd.read_file(opj(DATA_DIR, cropland_shapefile)) 

# # FOCUS ON ONLY VINEYARDS AND ORCHARDS
# crop_focus = ["D | DECIDUOUS FRUITS AND NUTS", "V | VINEYARD", "C | CITRUS AND SUBTROPICAL"]
# tree_crops = cropmap[cropmap['DWR_Standa'].isin(crop_focus)== True] # Compost market end-use

# out = r"treecrops.shp"
# tree_crops.to_file(driver='ESRI Shapefile', filename=opj(DATA_DIR, out))

# crops = gpd.read_file(opj(DATA_DIR, 'treecrops/treecrops.shp'))
# identify centroid for use in node assignment
# crops['centroid'] = crops['geometry'].centroid

# MINIMIZE THIS TO SOMETHING MORE MANAGABLE! >> GRAPES & ALMONDS
# crops[(crops['Crop2014'] == 'Grapes') | (crops['Crop2014'] == 'Almonds')]
hvcrops = gpd.read_file(opj(DATA_DIR, 'treecrops/hv_treecrops.shp'))
# identify centroid for use in node assignment
hvcrops['centroid'] = hvcrops['geometry'].centroid

hvcrops['area_ha'] = hvcrops['Acres']/2.471 # convert area in acres to hectares
hvcrops['capacity_tons'] = hvcrops['area_ha'] * 36.83
#############################################



##### EJ ###################################
cal_EJ = gpd.read_file(opj(DATA_DIR,
                          calenviroscreen_shapefile))
cal_EJ.to_crs(epsg=4326) # make sure this is in the right projection
#############################################



##### OPP ZONES ##############################
opp_zones = gpd.read_file(opj(DATA_DIR,
                          oppzones_shapefile))
opp_zones = opp_zones[opp_zones['STATENAME'] == "California"]
opp_zones = opp_zones.to_crs(epsg=4326) # make sure this is in the right projection
#############################################


##### AIR DISTRICTS ##########################
air_districts = gpd.read_file(opj(DATA_DIR, air_district_shapefile))
air_districts = air_districts.to_crs(epsg=4326)
#############################################

##############################################################################################
# LOAD MATRICES FROM ROAD NETWORK (see roadnetworkprep.py for details on creation)
# print('LOADING ROAD MATRICES')

# make sure directory is consistent on REMOTE SERVER
with open('outputs/node_pts.p', 'rb') as f:
    nodes = pickle.load(f)

with open('outputs/adjacency.p', 'rb') as f:
    L = pickle.load(f)

with open('outputs/distance.p', 'rb') as f:
    Distance = pickle.load(f)


print("DATA LOADED & CLEANED")

##############################################################################################
### CONNECT DATA POINTS TO ROAD NETWORK!! ######
##############################################################################################


# ASSOCIATE MSW PTS to NODE ON ROAD NETWORK 
# (RUN ONCE, THEN SAVE AND USE OVER)

# msw_node = []
# print("starting to associate msw pts to road nodes")
# for p, point in enumerate(msw['geometry']):
#     temp = []
#     if p % 100 == 0:
#         print("STILL RUNNING: ", p)
#     for i, node in enumerate(nodes):
#         dist = np.sqrt((point.x - node.x)**2 + (point.y - node.y)**2)
#         temp.append(dist)
#     nn = np.argmin(temp)
#     msw_node.append(nn)

# # These take a long time - SAVE THEM!!! 
# with open('outputs/msw_node.p', 'wb') as f:
#     pickle.dump(msw_node, f)

# print("msw_node saved")
###########     #############     #############     #############     #############     
# instead of re-running - load saved file!
# with open('outputs/msw_node.p', 'rb') as f:
#     msw_node = pickle.load(f)


# # ASSOCIATE EXISTING FACILITIES   
# composter_node = []
# print("starting to associate existing comopsters to road nodes")
# for p, point in enumerate(composters['geometry']):
#     temp = []
#     if p % 100 == 0:
#         print("CMP - STILL RUNNING: ", p)
#     for i, node in enumerate(nodes):
#         dist = np.sqrt((point.x - node.x)**2 + (point.y - node.y)**2)
#         temp.append(dist)
#     nn = np.argmin(temp)
#     composter_node.append(nn)

# # ASSOCIATE GL and CL TO NEAREST NODE? (use CENTROID OF POLYGON
# gl_node = []
# for p, point in enumerate(rangelands['centroid']):
#     temp = []
#     if p % 100 == 0:
#         print("GL - STILL RUNNING: ", p)
#     for i, node in enumerate(nodes):
#         dist = np.sqrt((point.x - node.x)**2 + (point.y - node.y)**2)
#         temp.append(dist)
#     nn = np.argmin(temp)
#     gl_node.append(nn)
###########     #############     #############     #############     #############     


###########     #############     #############     #############     #############     
# print('STARTING CROP ASSOCIATION - SO SLOW')
# sub_crop_node = []
# for p, point in enumerate(sub_crops['centroid']):
#     temp = []
#     if p % 100 == 0:
#         print("CROP - STILL RUNNING: ", p)
#     for i, node in enumerate(nodes):
#         dist = np.sqrt((point.x - node.x)**2 + (point.y - node.y)**2)
#         temp.append(dist)
#     nn = np.argmin(temp)
#     sub_crop_node.append(nn)

# # # These take a long time - SAVE THEM!!! 
# with open('outputs/sub_crop_node.p', 'wb') as f:
#     pickle.dump(sub_crop_node, f)

# print("crop_node saved!!")
###########     #############     #############     #############     ############# 

# instead of re-running - load saved file!
# with open('outputs/crop_node.p', 'rb') as f:
#     crop_node = pickle.load(f)

with open('outputs/sub_crop_node.p', 'rb') as f:
    sub_crop_node = pickle.load(f)


# LOOK OUT ASSIGNED NODES w DATA IN TURN TO MAKE SURE THEY LOOK OKAY? 
# - THEY DON"T LOOK AMAZING ---- JUST EXPLAIN AS A 'LIMITATION'
# fig, ax = plt.subplots(ncols = 3, figsize = (18,8))
# # msw and nodes (plot each?)
# msw.plot(marker = 'o', color = 'm', edgecolor = 'white', label = ' MSW - TRUE',
#     ax = ax[0], alpha = 0.5)
# for i in range(len(msw_node)):
#     if i % 200 == 0:
#         print("MSW -- STILL THINKING: ", i)
#     n = msw_node[i]
#     _ = ax[0].plot(nodes[n].x, nodes[n].y, marker = 'o', color = 'c', alpha = 0.5)

# ## PLOT - MSW_NODE
# composters.plot(marker = 'o', color = 'black', edgecolor = 'white', 
#     label = "Compost Facility - TRUE", ax = ax[1], alpha = 0.5)
# ## PLOT - COMPOSTER_NODE
# for i in range(len(composter_node)):
#     if i % 100 == 0:
#         print("COMPOSTER -- STILL THINKING: ", i)
#     n = composter_node[i]
#     _ = ax[1].plot(nodes[n].x, nodes[n].y, marker = 'o', color = 'y', alpha = 0.5)
# # plot GL & CL
# plt.show()

##############################################################################################
# Fig XX : DATA SOURCES   //TODO
##############################################################################################


# fig, ax = plt.subplots(ncols = 3, figsize = (18,8))

# # divider = make_axes_locatable(ax)
# # cax = divider.append_axes("right", size="5%", pad=0.1)

# # for geom in california['geometry']: 
# #     if geom.type == 'Polygon':
# #         # plot normally
# # #         plt.plot(*df.loc[d, 'geometry'].exterior.xy, 'w-', linewidth =1.5)
# #         lat, lon = geom.exterior.xy
# # #         plt.plot(lat, lon, 'k--')
# #         ax.plot(*geom.exterior.xy, 'darkgrey', linewidth = 1.5)
# #     elif geom.type == 'MultiPolygon':
# #         for p in geom:
# #             ax.plot(*p.exterior.xy, 'darkgrey', linewidth =1.5)

# california.plot(color = 'white', edgecolor = 'darkgrey', ax = ax[0])
# road_network.plot(color = 'lightgrey', linestyle = '-', 
#                   linewidth = 1.5, label = "Roads", ax = ax[0], alpha = 0.9)
# #  THIS ONE FOR POINTS
# msw[msw['subtype'] == 'MSW_green'].plot(markersize = 'bdt', 
#          legend = True, ax = ax[0], alpha = 0.5, c = 'm')
# ax[0].plot([],[], 'mo', label = 'MSW (tons)')
# # THIS ONE FOR POLYGONS (CHOROPLETH)
# # tract_sum_geo.plot(column = 'wt', ax = ax, cmap = 'Purples', 
# #                    edgecolor = 'white', legend = True, cax = cax)

# composters.plot(marker = 'o', color = 'black', edgecolor = 'white', label = "Compost Facility", 
#                 ax = ax[0], zorder = 10)
# # cbar.set_label('Org. Fraction MSW')
# ax[0].set_xlabel("Longitude")
# ax[0].set_ylabel("Latitude")
# ax[0].set_title('California MSW, Roads and Existing Facilities')
# ax[0].legend()



# # ADD OTHER DATA SOURCE -- hvcrops

# california.plot(color = 'white', edgecolor = 'darkgrey', ax = ax[1])
# road_network.plot(color = 'lightgrey', linestyle = '-', 
#                   linewidth = 1.5, label = "Roads", ax = ax[1], alpha = 0.9)
# composters.plot(marker = 'o', color = 'black', edgecolor = 'white', label = "Compost Facility", 
#                 ax = ax[1], zorder = 10)

# hvcrops = hvcrops.set_geometry('centroid')
# hvcrops.plot(color = 'blue', alpha= 0.6, ax = ax[1], label = 'HV Crops', 
#     markersize = hvcrops['capacity_tons']/5)

# rangelands = rangelands.set_geometry('centroid')
# rangelands.plot(color = "green", ax = ax[1], alpha = 0.6, label = 'Rangeland', 
#     markersize = rangelands['capacity_tons']/8000)
# # # oppzones
# # opp_zones.plot(color = 'pink', ax = ax[1], label = 'Opportunity Zones')
# # also plot air districts and EJ?
# ax[1].set_xlabel("Longitude")
# ax[1].set_ylabel("Latitude")
# ax[1].set_title('Suitable Grasslands and High Value Crops')
# ax[1].legend()




# road_network.plot(color = 'lightgrey', linestyle = '-', 
#                   linewidth = 1.5, label = "Roads", ax = ax[2], alpha = 0.9)
# composters.plot(marker = 'o', color = 'black', edgecolor = 'white', label = "Compost Facility", 
#                 ax = ax[2], zorder = 10)


# # # oppzones
# opp_zones.plot(color = 'pink', ax = ax[2], label = 'Opportunity Zones')
# air_districts.plot(facecolor = 'none', edgecolor = 'k', ax = ax[2])
# cal_EJ.plot(column = 'CIscoreP', cmap = 'RdYlGn_r', ax = ax[2])

# # also plot air districts and EJ?
# ax[2].set_xlabel("Longitude")
# ax[2].set_ylabel("Latitude")
# ax[2].set_title('Suitable Grasslands and High Value Crops')
# ax[2].legend()




# plt.show()
# fig.savefig('figures/datasources.png')


# //TODO - add third category?

# california.plot(facecolor="none", edgecolor = 'black', linestyle = '--', ax = ax)
# air_districts.plot(column = 'NAME', ax = ax)
# opp_zones.plot(color = 'pink', ax = ax[1], label = 'Opportunity Zones')
# cal_EJ.plot(column = 'CIscoreP', cmap = 'RdYlGn_r', ax = ax[2])

##############################################################################################
# SIMULATE RANDOM POINTS!!! PLOT MSW, ROADS, EXISTING FACILITIES
##############################################################################################
print("STARTING POINT SIM")

# OKAY SKIP THAT FOR NOW, start with loop that goes through 
# each point and adds up available feedstock, existing capacity, etc

# simulating random points:

# number of events to simulate
# N = 2000

# # AREA to cast random numbers in 
# # 10 degrees from -125
# lon = np.random.random(N) * 10 - 125
# # 10 degrees from 32
# lat = np.random.random(N) * 10 + 32

# # this reorganizes the points such that the input format
# # is consistent with what MultiPoint() expects
# potential_sites = MultiPoint(np.vstack((lon, lat)).T)

# # california (union of all conties for full state)
california_state =  gpd.GeoSeries(cascaded_union(california['geometry']))[0]

# # only keep sites within state boundary
# potential_sites = potential_sites.intersection(california_state)

# # print("ASSOCIATE ALL SIM POINTS WITH CLOSEST NODE IN ROAD NETWORK")
# # # ASSOCIATE EACH RANDOMIZED POINT TO NODE ON ROAD NETWORK
# # point_node = []
# # for p, point in enumerate(potential_sites):
# #     temp = []
# #     for i, node in enumerate(nodes):
# #         dist = np.sqrt((point.x - node.x)**2 + (point.y - node.y)**2)
# #         temp.append(dist)
# #     nn = np.argmin(temp)
# #     point_node.append(nn)
# with open('outputs/potential_sites.p', 'wb') as f:
#     pickle.dump(potential_sites, f)


with open('outputs/potential_sites.p', 'rb') as f:
    potential_sites = pickle.load(f)


##############################################################################################
# MAKE BUFFERS AND START CALCULATING!!!!!!!!!!
##############################################################################################

# (maybe wrap this into function to calculate radius throughout california!) //TODO
print("DEFINING BUFFERS")
# Calculate buffer around each point and get expected value of new site there!
#rad = deg * pi/180
lat = california_state.centroid.y * np.pi/180 # in radians

km_per_degree = np.cos(lat)*111.321

buffer_radius = buffer_km/km_per_degree # buffer_km defined by USER ABOVE



##############################################################################################

# raise Exception("ABOUT TO START CALCULATING SCORES!! ")

south_coast = air_districts[air_districts['NAME'] == 'South Coast']['geometry']

print("START CALCULATING SCORES for ****", len(potential_sites), "**** SITES")
# # CREATE EMPTY ARRAY FOR POTENTIAL SITES VALUES
# # site_results = np.zeros(len(potential_sites))
# site_results = []
ej_score = []

# # LOOP THROUGH ALL POINTS
for p, point in enumerate(potential_sites):
    if p % 10 == 0:
        print("looping through site number: ", p)
#     # value = 0
#     # BUFFER AROUND point
#     buffer = point.buffer(buffer_radius)
#     # blat, blon = buffer.exterior.xy
#     # lat, lon = point.x, point.y
#     # ax.plot(lat, lon, 'kx')
#     # ax.plot(blat, blon, 'k--')
#     ##### nearest_node ######
#     # nn = point_node[p]
#     ##### MSW (TON OF FEEDSTOCK) #####
#     msw_tons = 0
#     msw_dist = 0
#     for f, geom in enumerate(msw['geometry']):
#         if geom.intersection(buffer):
# #             print('FOUND ONE', p, f)
# #             print(f)
#             # ax.scatter(geom.x, geom.y, c = 'm', s = (msw.loc[f, 'total_wt'])/10, 
#             #            alpha = '0.2')
# #             geom.plot(markersize = 'total_wt' ax = ax, alpha = 0.5)
#             msw_tons += msw.iloc[f, :]['wt']
#             msw_dist += np.sqrt((geom.x - point.x)**2 + (geom.y - point.y)**2)
#     feedstock_score = msw_tons * msw_dist
#     ##### COMPOST FACILITIES (CAPACITY) ######
#     comp_value = 0
#     comp_dist = 0
#     for c, geom in enumerate(composters['geometry']):
# #         print(c)
# #         print(geom.type)
#         if geom.intersection(buffer):
#             comp_value += -(composters.iloc[c, :]['cap_ton'])
#             # ax.scatter(geom.x, geom.y, marker = 'o', color = 'black', 
#             #            edgecolor = 'white', alpha = '0.9')
#             comp_dist += np.sqrt((geom.x - point.x)**2 + (geom.y - point.y)**2)
#     comp_score = comp_value * comp_dist
#     ##### MARKET CAPACITY (AREA?) ######
#     market_value = 0
#     market_dist = 0
#     for m, geom in enumerate(hvcrops['centroid']):
#         if geom.within(buffer):
#             # print("hv crops")
#             market_value += hvcrops.iloc[m, :]['capacity_tons']
#             market_dist += np.sqrt((geom.x - point.x)**2 + (geom.y - point.y)**2)
#     market_score = market_value * market_dist
#     ##### AIR QUALITY BINARY ######
#     # aq_score = np.NaN
#     for geom in south_coast:
#         if point.within(geom):
#             print("IN SOUTH COAST")
#             aq_score = 0
#         else:
#             aq_score = 1
#     ##### EJ BINARY ######
    for t, geom in enumerate(cal_EJ['geometry']):
        if geom.contains(point):
            # grab EJ score as a percent (HIGHER IS BAD!)
            # ej_score = (cal_EJ.iloc[t, :]['CIscore'])/100
            ej_score.append((cal_EJ.iloc[t, :]['CIscore'])/100)
        else:
            ej_score.append(0)
#     ##### OPP ZONE BINARY ######
#     for o, geom in enumerate(opp_zones['geometry']):
#         if geom.contains(point):
#             opp_score = 1
#         else:
#             opp_score = 0
#     # APPEND ALL ! 
#     site_results.append([feedstock_score, market_score, comp_score, aq_score, ej_score,opp_score, 
#         msw_tons, msw_dist, comp_value, comp_dist, market_value, market_dist])
    ## AT END, APPEND ALL OF THESE TO MY LIST

## NOTE: THIS TAKES ABOUT 12 min on my local machine to run - check server? //TODO

# save site results to plot later
# with open('outputs/site_results.p', 'wb') as f:
#     pickle.dump(site_results, f)

with open('outputs/site_results.p', 'rb') as f:
    site_results = pickle.load(f)


# ax.plot([], [], 'kx', label = 'Potential Site')    
# ax.plot([], [], 'k--', label = 'Buffer Zone')   
# ax.plot([], [], 'mo', alpha = 0.5, label = 'MSW generation')
# ax.plot([], [], marker = 'o', color = 'black', label = 'Existing Facility', 
#         linestyle = 'None')
# ax.set_xlabel("Longitude")
# ax.set_ylabel("Latitude")
# ax.legend()
    
# CHECK SITE RESULTS    
# site_results

##############################################################################################
# CALCULATE SCORES BASED ON RESULTS
##############################################################################################

# order: [feedstock_score, market_score, comp_score, aq_score, ej_score, opp_score, 
#          msw_tons, msw_dist, comp_value, comp_dist, market_value, market_dist]

raise Exception("HALLLLLA")

print("STARTING POLICY EVALUATION")

# p 0 : just msw and competing facilities
p0_score = np.zeros(len(potential_sites))
# loop through all and calculate
for p in range(len(site_results)):
    x = site_results[p]
    # p0 score made up of feedstock and competition, 
    p0_score[p] = x[0] + x[2] #//TODO ADD PRICING FACTORS?

#sort!
p0_idx = np.argsort(p0_score) # returns the indices
# grab 100 best sites
p0_idx = p0_idx[-100:]
# use this to grab the potential sites?

p0_sites = []
for p, point in enumerate(potential_sites):
    # print(p)
    if p in p0_idx:
        p0_sites.append(point)

p0_sites = MultiPoint(p0_sites)



# policy objective one: monies
p1_score = np.zeros(len(potential_sites))
# loop through all and calculate
for p in range(len(site_results)):
    x = site_results[p]
    # p1 score made up of feedstock, market and competition, 
    p1_score[p] = x[0] + x[1] + x[2] #//TODO ADD PRICING FACTORS?

#sort!
p1_idx = np.argsort(p1_score) # returns the indices
# grab 100 best sites
p1_idx = p1_idx[-100:]
# use this to grab the potential sites?

p1_sites = []
for p, point in enumerate(potential_sites):
    # print(p)
    if p in p1_idx:
        p1_sites.append(point)

p1_sites = MultiPoint(p1_sites)

##############################################################################################

# policy objective two: ADD EJ
p2_score = np.zeros(len(potential_sites))
# loop through all and calculate
for p in range(len(site_results)):
    x = site_results[p]
    # p2 score made up of feedstock, market and competition, 
    # TIMES EJ score
    p2_score[p] = (x[0] + x[1] + x[2]) * (1 - ej_score[4]) 

#sort!
p2_idx = np.argsort(p2_score) # returns the indices
# grab 100 best sites
p2_idx = p2_idx[-100:]
# use this to grab the potential sites?

p2_sites = []
for p, point in enumerate(potential_sites):
    # print(p)
    if p in p2_idx:
        p2_sites.append(point)

p2_sites = MultiPoint(p2_sites)

##############################################################################################


# policy objective three: EJ and OPP SCORE and AQ
p3_score = np.zeros(len(potential_sites))
# loop through all and calculate
for p in range(len(site_results)):
    x = site_results[p]
    # p3 score made up of feedstock, market and competition, 
    # TIMES EJ score & Opp zone indicator
    p3_score[p] = (x[0] + x[1] + x[2]) * (1 - ej_score[4])  * x[5] * x[3]

#sort!
p3_idx = np.argsort(p3_score) # returns the indices
# grab 100 best sites
p3_idx = p3_idx[-100:]
# use this to grab the potential sites?

p3_sites = []
for p, point in enumerate(potential_sites):
    # print(p)
    if p in p3_idx:
        p3_sites.append(point)

p3_sites = MultiPoint(p3_sites)

# raise Exception(" HAVE RESULTS TO PLOT!")



##############################################################################################
# FIG X. RESULTS MAPS
##############################################################################################
# //TODO polish this up! 

f, ax = plt.subplots(ncols = 2, nrows =2, sharey = True, figsize = (12, 12))
for point in potential_sites:
    lat, lon = point.x, point.y
#     print(type(point))
    for a in range(2):
            for b in range(2):
                _ = ax[a,b].plot(lat, lon, 'kx')
                _ = california.plot(color = 'white', edgecolor = 'darkgrey', ax = ax[a,b])
#     for geom in opp_zones['geometry']:
#         if point.intersection(geom):
#             glat, glon = geom.exterior.xy
#             ax[0].plot(glat, glon, color = 'pink', alpha = '0.6')
print('plotted mains')
# panel 0
for p in p0_sites:
    _ = ax[0,0].plot(p.x, p.y, marker = '*', color = 'r')

print('plotted p0')
# panel 1
for p in p1_sites:
    _ = ax[0,1].plot(p.x, p.y, marker = '*', color = 'r')
print('plotted p1')

# panel 2
for p in p2_sites:
    _ = ax[1,0].plot(p.x, p.y, marker = '*', color = 'r')
print('plotted p2')

# panel 3
for p in p3_sites:
    _ = ax[1,1].plot(p.x, p.y, marker = '*', color = 'r')

print('plotted p3')

ax[0,0].set_title("Policy 0")
ax[0,1].set_title("Policy 1")
ax[1,0].set_title("Policy 2")
ax[1,1].set_title("Policy 3")

# could highlight some the sites that are unique to different situations?


for a in range(2):
    for b in range(2):        
        ax[a,b].plot([], [], 'kx', label = 'Simulated Potential Site')
        ax[a,b].plot([], [], 'r*', label = 'Optimal Location')
        ax[a,b].set_xlabel("Longitude")
        ax[a,b].set_ylabel("Latitude")
        ax[a,b].legend()   

plt.show()

fig.savefig('figures/policyresults.png')

##############################################################################################
# FIG XX. HISTOGRAM
##############################################################################################

# //TODO
# Plot histogram of something?? -- histogram of all msw_tons, msw_dist, market_value, market_dist

# reminder : # order: [feedstock_score, market_score, comp_score, aq_score, ej_score, opp_score, 
#          msw_tons, msw_dist, comp_value, comp_dist, market_value, market_dist]


msw_tons = []
msw_dist = []
market_value = []
market_dist = []

for s in range(len(site_results)):
    msw_tons.append(site_results[s][6])
    msw_dist.append(site_results[s][7])
    market_value.append((site_results[s][10]/36.83))
    market_dist.append(site_results[s][11])


fig, ax = plt.subplots(2,2, figsize = (10,8))

ax[0,0].hist(msw_tons, bins='auto', color='#7bccc4',
                            alpha=0.7, rwidth=0.85)
ax[0,0].set_title("Feedstock within 75km")
ax[0,0].set_xlabel("Organic MSW (Tons)")

ax[0,1].hist(msw_dist, bins='auto', color='#43a2ca',
                            alpha=0.7, rwidth=0.85)
ax[0,1].set_title("Distance to MSW Feedstock")
ax[0,1].set_xlabel("Distance (km)")

ax[1,0].hist(market_value, bins= 30, color='#bae4bc',
                            alpha=0.7, rwidth=0.85)
ax[1, 0].set_title("End Use Market Value within 75km")
ax[1,0].set_xlabel("High-Value Cropland (Hectares)")

ax[1,1].hist(market_dist, bins=30, color='#43a2ca',
                            alpha=0.7, rwidth=0.85)
ax[1, 1].set_title("Distance to High Value Cropland")
ax[1,1].set_xlabel("Distance (km)")

for i in (range(2)):
    for j in (range(2)):
        ax[i,j].set_ylabel("Count")
plt.tight_layout()
plt.show()
fig.savefig('figures/histos.png')


##############################################################################################

# HALLA
f, ax = plt.subplots(figsize = (8,8))
california.plot(color = 'white', edgecolor = 'darkgrey', ax = ax)
for p, point in enumerate(potential_sites):
    if p % 10 == 0:
        print("looping through site number: ", p)
    # value = 0
    # BUFFER AROUND point
    buffer = point.buffer(buffer_radius)
    blat, blon = buffer.exterior.xy
    lat, lon = point.x, point.y
    ax.plot(lat, lon, 'kx')
    ax.plot(blat, blon, 'k--')

plt.show()











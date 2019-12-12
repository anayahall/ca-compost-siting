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
DATA_DIR = "/Users/anayahall/Box/compostsiting/data"

# SERVER DATA DIR
# DATA_DIR = "data"

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

# SOCIAL/ECONOMIC/POLITICAL
calenviroscreen_shapefile = "calenviroscreen/CESJune2018Update_SHP/CES3June2018Update_4326.shp"
oppzones_shapefile= "Opportunity Zones/8764oz.shp"
# //TODO add air quality districts

## USER-DEFINED PARAMETERS
buffer_km = 75 # //TODO COULD MAKE THIS A USER INPUT SOMEWHERE ELSE! 

print("DATA READY TO LOAD")
##############################################################################################
# LOAD DATA
##############################################################################################

# California counties
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

# Municipal Solid Waste (points)
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
# msw_sum =  msw.groupby(['County', 'subtype']).sum() # may combine??? //TODO?
msw_total = msw.groupby(['ID', 'County']).sum()

# Roads
# road_network = gpd.read_file(opj(DATA_DIR, 
#                                  roads_shapefile))
# not necessary --- bring these in as adjacency matrices later!!

# Composting Facilities
composters = gpd.read_file(opj(DATA_DIR,
                                compost_facilities_shapefile))
# change capacity metric to tons!
composters['cap_ton'] = composters['cap_m3']*0.58


# Rangelands
rangelands = gpd.read_file(opj(DATA_DIR,
                              rangelands_shapefile))
rangelands = rangelands.to_crs(epsg=4326) # make sure this is in the right projection

# EJ
cal_EJ = gpd.read_file(opj(DATA_DIR,
                          calenviroscreen_shapefile))
cal_EJ.to_crs(epsg=4326) # make sure this is in the right projection

opp_zones = gpd.read_file(opj(DATA_DIR,
                          oppzones_shapefile))
opp_zones = opp_zones[opp_zones['STATENAME'] == "California"]

opp_zones = opp_zones.to_crs(epsg=4326) # make sure this is in the right projection


msw = gpd.read_file(opj(DATA_DIR,
                  msw_shapefile))

# filter to just keep food and green waste (subject of regulations)
msw = msw[(msw['subtype'] == "MSWfd_wet_dryad_wetad") | (msw['subtype'] == "MSWgn_dry_dryad")]
msw['subtype'].replace({'MSWfd_wet_dryad_wetad': 'MSW_food', 
                        'MSWgn_dry_dryad': 'MSW_green'}, inplace = True)

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

print("DATA LOADED")
##############################################################################################
# Fig XX : PLOT MSW, ROADS, EXISTING FACILITIES --> SEE SLIDES //TODO
##############################################################################################

# fig, ax = plt.subplots(figsize = (8,8))

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
# california.plot(color = 'white', edgecolor = 'darkgrey', ax = ax)
# road_network.plot(color = 'grey', linestyle = '-', 
#                   linewidth = 1.5, label = "Roads", ax = ax, alpha = 0.9)

# #  THIS ONE FOR POINTS
# msw[msw['subtype'] == 'MSW_green'].plot(markersize = 'bdt', 
#          legend = True, ax = ax, alpha = 0.5, c = 'm')
# ax.plot([],[], 'mo', label = 'MSW (tons)')
# # THIS ONE FOR POLYGONS (CHOROPLETH)
# # tract_sum_geo.plot(column = 'wt', ax = ax, cmap = 'Purples', 
# #                    edgecolor = 'white', legend = True, cax = cax)

# composters.plot(marker = 'o', color = 'black', edgecolor = 'white', label = "Compost Facility", 
#                 ax = ax, zorder = 10)
# # cbar.set_label('Org. Fraction MSW')

# # opp_zones.plot(color = 'm', ax = ax)
# # rangelands.plot(color = "Green", ax = ax)
# ax.set_xlabel("Longitude")
# ax.set_ylabel("Latitude")
# ax.set_title('California MSW, Roads and Existing Facilities')
# ax.legend()

##############################################################################################
# SIMULATE RANDOM POINTS!!! PLOT MSW, ROADS, EXISTING FACILITIES
##############################################################################################
print("STARTING POINT SIM")

# OKAY SKIP THAT FOR NOW, start with loop that goes through 
# each point and adds up available feedstock, existing capacity, etc

# simulating random points:

# number of events to simulate
N = 1000

# AREA to cast random numbers in 
# 10 degrees from -125
lon = np.random.random(N) * 10 - 125
# 10 degrees from 32
lat = np.random.random(N) * 10 + 32

# this reorganizes the points such that the input format
# is consistent with what MultiPoint() expects
potential_sites = MultiPoint(np.vstack((lon, lat)).T)

# california (union of all conties for full state)
california_state =  gpd.GeoSeries(cascaded_union(california['geometry']))[0]

# only keep sites within state boundary
potential_sites = potential_sites.intersection(california_state)


##############################################################################################
# plot to make sure this looks like I expect --> SEE SLIDES
##############################################################################################

# f, ax = plt.subplots(ncols = 3, sharey = True, figsize = (15, 6))
# for point in potential_sites:
#     lat, lon = point.x, point.y
# #     print(type(point))
#     for a in range(3):
#         ax[a].plot(lat, lon, 'kx')
#         california.plot(color = 'white', edgecolor = 'darkgrey', ax = ax[a])
# #     for geom in opp_zones['geometry']:
# #         if point.intersection(geom):
# #             glat, glon = geom.exterior.xy
# #             ax[0].plot(glat, glon, color = 'pink', alpha = '0.6')
      

# # ADD TO THIS FOR 'PRELIMINARY RESULTS'
# # rangeland locations

# rangelands.plot(color = "limegreen", ax = ax[0], alpha = 0.6, label = 'Rangeland')
# # oppzones
# opp_zones.plot(color = 'pink', ax = ax[1], label = 'Opportunity Zones')

# # close to roads???    
# # road_network.plot(color = 'c', linestyle = '-', 
# #                   linewidth = 0.8, label = "Roads", ax = ax[2], alpha = 0.7)   
# # EJ
# cal_EJ.plot(column = 'CIscoreP', cmap = 'RdYlGn_r', ax = ax[2])

# ax[0].set_title("Grazed Grassland")
# ax[1].set_title("Economic Opportunity ")
# ax[2].set_title("Road Distance")

# for a in range(3):        
#     ax[a].plot([], [], 'kx', label = 'Simulated Potential Site')
#     ax[a].set_xlabel("Longitude")
#     ax[a].set_ylabel("Latitude")
#     ax[a].legend()   
    
# plt.show()

##############################################################################################
# MAKE BUFFERS AND START CALCULATING!!!!!!!!!!
##############################################################################################

# (maybe wrap this into function to calculate radius throughout california!) //TODO

# Calculate buffer around each point and get expected value of new site there!
#rad = deg * pi/180
lat = california_state.centroid.y * np.pi/180 # in radians

km_per_degree = np.cos(lat)*111.321

buffer_radius = buffer_km/km_per_degree # buffer_km defined by USER ABOVE


##############################################################################################
# LOAD MATRICES FROM ROAD NETWORK (see roadnetworkprep.py for details on creation)
print('LOADING ROAD MATRICES')

# //TODO - make sure directory is consistent on REMOTE SERVER
with open('outputs/node_pts.p', 'rb') as f:
    nodes = pickle.load(f)

with open('outputs/adjacency.p', 'rb') as f:
    L = pickle.load(f)

with open('outputs/distance.p', 'rb') as f:
    Distance = pickle.load(f)
##############################################################################################

# ###### PLOT ###########################
# f, ax = plt.subplots(figsize = (8,8))
# california.plot(color = 'white', edgecolor = 'darkgrey', ax = ax)

raise Exception("ABOUT TO START CALCULATING SCORES!! TROUBLESHOOT FROM HERE")

print("START CALCULATING SCORES")
# CREATE EMPTY ARRAY FOR POTENTIAL SITES VALUES
site_results = np.zeros(len(potential_sites))

# LOOP THROUGH ALL POINTS
for p, point in enumerate(potential_sites):
    if p % 100 == 0:
        print("looping through site number: ", p)
    value = 0
    # BUFFER AROUND point
    buffer = point.buffer(buffer_radius)
    # blat, blon = buffer.exterior.xy
    # lat, lon = point.x, point.y
    # ax.plot(lat, lon, 'kx')
    # ax.plot(blat, blon, 'k--')
    ##### MSW (TON OF FEEDSTOCK) #####
    for f, geom in enumerate(msw['geometry']):
        if geom.intersection(buffer):
#             print('FOUND ONE', p, f)
#             print(f)
            # ax.scatter(geom.x, geom.y, c = 'm', s = (msw.loc[f, 'total_wt'])/10, 
            #            alpha = '0.2')
#             geom.plot(markersize = 'total_wt' ax = ax, alpha = 0.5)
            value += msw.iloc[f, :]['wt']
            dist = np.sqrt((geom.x - point.x)**2 + (geom.y - point.y)**2)
    ##### COMPOST FACILITIES (CAPACITY) ######
    for c, geom in enumerate(composters['geometry']):
#         print(c)
#         print(geom.type)
        if geom.intersection(buffer):
            value += -(composters.iloc[c, :]['cap_ton'])
            # ax.scatter(geom.x, geom.y, marker = 'o', color = 'black', 
            #            edgecolor = 'white', alpha = '0.9')
            dist = np.sqrt((geom.x - point.x)**2 + (geom.y - point.y)**2)
	###### CLOSEST NODE? THEN USE DIJSTRKA"S ~~~~~~~~~~
	# this 
	# np = nearest_points(point, nodes[1])[1]
    ###### dist
    if value > 100:
#         print('YAY')
        site_results[p] = value

## NOTE: THIS TAKES ABOUT 12 min on my local machine to run - check server? //TODO

test = []
for point in potential_sites:
    nn = np.argmin(nearest_points(point, n) for n in nodes)
    test.append(nn)







# save site results to plot later
with open('site_results.p', 'wb') as f:
    pickle.dump(site_results, f)

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

#  //TODO
# make sure considering all of the things
# and saving
# sort 50 - 100? pick size somehow?
# plot the ones based on different cats
# could save each value as field and then use weighting to determine score

##############################################################################################
# FIG X. RESULTS
##############################################################################################
# //TODO
# Plot histogram of something
# map viz of different categories
# make user input? 



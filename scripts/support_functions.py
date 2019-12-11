# supporting functions
import numpy as np

##############################################################################################

# function to group by region
def add_region_variable(df, county_column):
    '''
    Function to add a region category column to existing california dataframe (or geodataframe)
    Requires a dataframe with a column with county names and what that column is called
    Returns the same data frame with a new column describing region
    
    
    Regional categories based on CalRecycle's recommendations
    (https://www.calrecycle.ca.gov/LGCentral/Summaries/Regional/Regions/)
    
    '''
    
    df['Region'] = np.NaN

    BayArea = ['BayArea', 'Alameda', 'Contra Costa', 'Marin', 'Napa', 'San Francisco',
              'San Mateo', 'Santa Clara', 'Solano', 'Sonoma']
    CentralCoast = ['CentralCoast', 'Monterey', 'San Benito', 'San Luis Obispo',
                   'Santa Barbara', 'Santa Cruz']
    CentralValleyN = ['CentralValleyNorth', 'Butte', 'Colusa', 'Glenn', 'Placer', 
                    'Sacramento', 'Shasta', 'Sutter', 'Tehama', 'Yolo', 'Yuba']
    CentralValleyS = ['CentralValleySouth', 'Fresno', 'Kern', 'Kings', 'Madera', 'Merced', 'San Joaquin',
                     'Stanislaus', 'Tulare']
    CoastalN = ['CoastalNorth', 'Del Norte', 'Humboldt', 'Lake', 'Mendocino']
    MountainN = ['MountainNorth', 'Lassen', 'Modoc', 'Nevada', 'Plumas', 'Sierra', 'Siskiyou',
                'Trinity']
    MountainS = ['MountainSouth','Alpine', 'Amador', 'Calaveras', 'El Dorado', 'Inyo', 'Mariposa', 'Mono', 
                'Tuolumne']
    SouthernCalCoastal = ['SoCalCoastal', 'Los Angeles', 'Orange', 'San Diego', 'Ventura']
    SouthernCalInland = ['SoCalInland', 'Imperial', 'Riverside', 'San Bernardino']


    regions = np.array([bayArea, CentralCoast, CentralValleyN,
                       CentralValleyS, CoastalN, MountainS,
                       MountainN, SouthernCalCoastal, SouthernCalInland])

    for r in regions:
    #     print(r, t)
    #     print(regions[r][0])
        for county in df[county_column]:
            if np.isin(county, r):
    #             print(county, ' found in region : ', r[0])
                df.loc[df[county_column] == county,
                                    'Region'] = r[0]

    return df


##############################################################################################

# REQUIRES DISTANCE_NETWORK TO BE ALREADY MADE!!!!

def shortest_path(distance_network = Distance, k0, k_final): # change presets as desired!
    """
    uses djisktra's algorithm to calculate the shortest path between defined nodes
    given a cost-distance matrix
    
    returns path, which can then be used for plotting!
    """
    
    # k0 = int(input('Station for facility?  Enter 1 to ' + str(len(stations)) + ':'))
    
    # D(i) = 'minimum distance to source location' [initialize as 'np.inf' for all elements except zero at source]
    D = np.full(len(stations), np.inf)
    D[k0] = 0

    # P(i) = 'parent node', keeps track of location where you jsut were [initialized as 'NaN' everywhere]
    P = np.full(len(stations), np.NaN)

    # P(i) = 'parent node', keeps track of location where you jsut were [initialized as 'NaN' everywhere]
    I = np.zeros(len(stations))

    # thrid, ITERATE the following until I(i) = 1 (while I == 0)

    # pick starting node (above D[0])= 0 determines start)

    # repeat a-d until I(i) = 1 for all i, except last
    while np.sum(I) < len(I)-1: #np.any(I) == 0: 
    # (a) select the node 'j' with the minimum value for D(i=j) among all i where I(i=j) == 0.
        J =  np.where(I == 0)[0]
        j = J[np.argmin(D[J])]

    # (b) set I(i=j) = 1
        I[j] = 1

        K = []
    # (c) Identify each node 'k' connected to 'j' where I(i=k) = 0
        for k in range(L.shape[0]):
            if (L[j,k] == 1) and (I[k] == 0):
                K.append(k)

    # (d) IF D[j] + Distance[j,k] < D(k):
            # replace D(k) = D(j) + Distance[j,k] 
            # and P(k) = j 
        for k in K:
            if D[j] + Distance[j,k] < D[k]:
                D[k] = D[j] + Distance[j,k]
                P[k] = j
                
    path = [k_final]

    while path[-1] != k0:
        k = int(P[path[-1]])
        path.append(k)

    # fig, ax = plt.subplots(ncols = 2, figsize = (15, 5))
    # # plot all railroads like normal
    # for i in range(len(df)):
    # #     line_lats, line_lons = df['geometry'][i].xy
    #     ax[0].plot(df['geometry'][i].xy[0], df['geometry'][i].xy[1], '--k', alpha = 0.8)

    # c = ax[0].scatter(stations[:,0], stations[:,1], marker = 'o', c = D)
    # ax[0].plot([],[], '--k', alpha = 0.8, label = 'Railroad')
    # ax[0].legend()
    # cbar = plt.colorbar(c, ax = ax[0])
    # cbar.set_label('Distance')
    # ax[0].set_xlabel("Longitude")
    # ax[0].set_ylabel("Latitude")
    # ax[0].set_title("Railroad Network Relative to Station {}".format(k0))
    
    # # get rid of inf for plotting
    # D_real = D[D!=np.inf]

    # # PLOT HISTOGRAM OF DISTANCES
    # ax[1].hist(D_real, density = True, bins = 30, histtype='stepfilled', 
    #          edgecolor='none', label = 'Distances', color = 'purple')
    # ax[1].set_title("Histogram of Distances from Station {}".format(k0))
    # ax[1].set_xlabel("Distance")
    # ax[1].set_ylabel("Count")

 
    return D



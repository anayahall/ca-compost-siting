# supporting functions
import numpy as np


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


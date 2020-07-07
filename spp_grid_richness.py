import pandas as pd
import geopandas as gpd

# read in csv files, renaming columns to be used
df = pd.read_csv("rainforest_lichen.csv",encoding='latin-1')
df = df.rename(columns={'Sample Spatial Reference':'osgr',
                       'Recommended Taxon Name/Attribute':'taxon'})

#function to assign spatial precision related to len of osgr
def func(row):
    if len(row['osgr']) == 12:
        return 1
    elif len(row['osgr']) == 10:
        return 10
    elif len(row['osgr']) == 8:
        return 100 
    elif len(row['osgr']) == 6:
        return 1000
    elif len(row['osgr']) == 4:
        return 10000
    elif len(row['osgr']) == 2:
        return 100000

# corrects easting northing to centre of grid ref, removes any 2 or 0 figure osgr's
df['precision'] = df.apply(func,axis=1)
df = df[df.precision <= 1000] 
df['midpoint'] = df['precision']/2.0
df['easting'] = df['easting'] + df['midpoint']
df['northing'] = df['northing'] + df['midpoint']

# converts to geodataframe
spp_point = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.easting,df.northing))
spp_point.crs = "EPSG:27700"

# reads in grid and performs spatial join with geodataframe
grid = gpd.read_file("no_zoo.gpkg")
grid_merge = gpd.sjoin(grid,spp_point,how='left',op='contains')

# creates cross_tab with grid_id and taxon, clipping to max of 1 to create binary 0/1 grid
cross_tab = pd.crosstab(grid_merge.grid_id,grid_merge.taxon)
cross_tab = cross_tab.clip(0,1)

# converts to int type for readability
for column in cross_tab.columns:
    if cross_tab[column].dtype == 'float64':
        cross_tab[column] = cross_tab[column].astype('int64')
    else:
        pass

# sums total number of unique spp per grid
cross_tab['spp_total'] = cross_tab[0::].sum(axis=1)
    
# writes as csv files
cross_tab.to_csv("lichen_matrix_v1.00.csv",encoding='utf-8')

# creates new df comprised only of 'total' column
total = cross_tab['spp_total']

# joins back to grid file using 'grid_id' as join key on both frames
shape_merge = grid.merge(total, left_on='grid_id',right_on='grid_id', how = 'left')

# fills null values with 0s and converts to integer
shape_merge['spp_total'].fillna(0, inplace=True)
shape_merge['spp_total'] = shape_merge['spp_total'].astype('int64')

# outputs as file
shape_merge.to_file("spp_richness.gpkg", layer='spp_richness', driver='GPKG')
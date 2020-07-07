# species_mapping

Processes a csv file of species presence points (spp_points.csv) and creates presence/absence matrix for each unique species by predfined bounday file (grid.gpkg).

Makes extensive use of pandas and geopandas libraries.

It works in the following way:

reads in csv as pandas dataframe
assigns spatial resolution by length of osgr field
strips out records below spatial resolution threshold
centers retained records by adjusting xy values by midpoint
converts dataframe to geopandas geodataframe and assigns defined EPSG where necessary
performs spatial join between grid file and spp_points, assiging grid ref to each record
cross tabulate geodataframe plotting species id against grid ref, clipping to max of 1 so each species is counted once in a given grid
sums total number of unique species
rejoins cross tab to grid using grid_id as join field
converts NaN values to 0 and converts to integer for readability
outputs as gpkg 

###################################################################
#
# map geographic locations from a file (e.g., event log) to shapefile
# polygons
#
# jech
###################################################################

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from pathlib import Path

# read the shapefile
shpfile = Path('/home/user/GIS/BOEM/Offshore_Wind_Lease_Outlines.shp')
polygons_gdf = gpd.read_file(shpfile)

# read the data file
datafile = Path('/home/user/DX202301/event_log/DX202301_eventlog_clean.csv')
elog_df = pd.read_csv(datafile)

# much of this comes from Gemini
elog_df['geometry'] = elog_df.apply(
        lambda row: Point(row['lon_dd'], row['lat_dd']), axis=1
)
points_gdf = gpd.GeoDataFrame(elog_df, geometry='geometry')

# set a CRS for the points; appears to be somewhat arbitrary
points_gdf.set_crs(epsg=4326, inplace=True)
# compare the data CRS to the shapefile and change the data to the shapefile
# if they do not match
if points_gdf.crs != polygons_gdf.crs:
  points_gdf = points_gdf.to_crs(polygons_gdf.crs)

# find the polygons where each point is
# this does not retain the points that are not in polygons
# TBD: RETAIN ALL POINTS
matched_gdf = gpd.sjoin(points_gdf, polygons_gdf, how="inner", predicate="within")

# output the new data file
ofile = Path('/home/user/DX202301/event_log/DX202301_eventlog_match-lease-areas.csv')
matched_gdf.to_csv(ofile, index=False)



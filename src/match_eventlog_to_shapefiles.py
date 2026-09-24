###################################################################
#
# map geographic locations from a file (e.g., event-log) to shapefile
# polygons
#
# jech
###################################################################

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from pathlib import Path

# read the data file
datafile = Path('/home/user/DX202301/event_log/DX202301_eventlog.csv')
elog_df = pd.read_csv(datafile)

# read the wind lease outlines shapefile
shpfile = Path('/home/user/GIS/BOEM/Offshore_Wind_Lease_Outlines.shp')
lease_polygons_gdf = gpd.read_file(shpfile)

# read the OCS 1st Division polygons
shpfile = Path('/home/user/GIS/BOEM/OCS_Block_Polygons_1st_Division.shp')
div1_polygons_gdf = gpd.read_file(shpfile)

# read the OCS 2nd Division polygons
# geopandas is having trouble reading this file
#shpfile = Path('/home/user/GIS/BOEM/OCS_Block_Polygons_-_2nd_Division.shp')
#div2_polygons_gdf = gpd.read_file(shpfile)

# read the OCS 3rd Division polygons
# geopandas is having trouble reading this file
#shpfile = Path('/home/user/GIS/BOEM/OCS_Aliquot_16ths_Polygons_-_3rd_Division.shp')
#div3_polygons_gdf = gpd.read_file(shpfile)

# read the WTG shapefile
shpfile = Path('/home/user/GIS/BOEM/NOAA_Charts_WTG.shp')
WTG_gdf = gpd.read_file(shpfile)

# much of these lines comes from Gemini
# convert the event-log data to a geopandas dataframe
elog_df['geometry'] = elog_df.apply(
        lambda row: Point(row['lon_dd'], row['lat_dd']), axis=1 )
elog_points_gdf = gpd.GeoDataFrame(elog_df, geometry='geometry')

# set a CRS for the event-log points; appears to be somewhat arbitrary
elog_points_gdf.set_crs(epsg=4326, inplace=True)
# compare the data CRS to the shapefile and change the data to the shapefile
# if they do not match
if elog_points_gdf.crs != lease_polygons_gdf.crs:
  elog_points_gdf = elog_points_gdf.to_crs(lease_polygons_gdf.crs)

# match the event-log points to the lease area polygons
# this line does not retain the event-log points that are not in polygons
#matched_gdf = gpd.sjoin(elog_points_gdf, lease_polygons_gdf, how="inner", predicate="within")
# this does retain all the event-log points even if they are not in a polygon
# points not in a polygon have NaN for the polygon data
matched_gdf = gpd.sjoin(elog_points_gdf, lease_polygons_gdf, how="left", predicate="within")

# keep all the event-log points columns
keep_elog_points_col_names = elog_points_gdf.columns.tolist()

# the BOEM lease area shapefiles have more fields than we want to use, so select the columns to keep
lease_col_names = lease_polygons_gdf.columns.tolist()
keep_lease_col_names = ['LEASE_NUMB',
                        'PROTRACTIO',
                        'PROJECT_NA']
keep_col_names = keep_elog_points_col_names
[keep_col_names.append(cname) for cname in keep_lease_col_names]
matched_gdf = matched_gdf[keep_col_names].copy()

# the 1st-division protractions are actually provided in the lease-area polygons, so we only
# need to match those with the 1st division polygons
# Unfortunately, the column names change among BOEM files
# lease area protraction name = 'PROTRACTIO', 1st division protraction = 'PROT_NUM'.
# we'll use the 1st division name and number
matched_gdf.rename(columns = {'PROTRACTIO': 'PROT_NUM'}, inplace=True)
# remove the old column name
keep_col_names.remove('PROTRACTIO')

# get the protraction name from the 1st division shapefile based on the protraction number
# in the matched data frame
# rgn_code is a broad category. A = Atlantic
keep_1st_div_col_names = ['RGN_CODE',
                          'PROT_NAME',
                          'PROT_NUM']
# there seemed to be an issue with the geometry column for the different shapefiles, so
# remove it along with the other non-needed columns
div1_polygons_gdf = div1_polygons_gdf[keep_1st_div_col_names].copy()

# add the 1st division column names to keep to the overall keep list
[keep_col_names.append(cname) for cname in keep_1st_div_col_names]
# merge the data frames based on protaction name
matched_gdf = pd.merge(matched_gdf, div1_polygons_gdf, on='PROT_NUM', how='left')
# retain only the selected columns
matched_gdf = matched_gdf[keep_col_names].copy()

# clean up the the column names 
# in the BOEM shapefiles rename:
#  LEASE_NUMB to lease_number
#  PROJECT_NA to project_name
#  RGN_CODE to region_code
#  PROT_NAME to protraction_name
#  PROT_NUM to protraction_number
matched_gdf.rename(columns = {'LEASE_NUMB': 'lease_number',
                              'PROJECT_NA' : 'project_name',
                              'RGN_CODE' : 'region_code',
                              'PROT_NAME' : 'protraction_name',
                              'PROT_NUM' : 'protraction_number'}, inplace=True)

# match the nearest turbine (WTG) to each point
# maximum distance in meters
max_distance = 2000
# convert the coordinate system to UTM
matched_gdf = matched_gdf.to_crs(matched_gdf.estimate_utm_crs())
matched_gdf.set_crs(epsg=32619, inplace=True)
WTG_gdf = WTG_gdf.to_crs(matched_gdf.crs)
nn_gdf = gpd.sjoin_nearest(matched_gdf, WTG_gdf, how='left', distance_col='distance',
                           max_distance=max_distance)

# output the new data file
ofile = Path('/home/user/DX202301/event_log/DX202301_eventlog_match-BOEM.csv')
#matched_gdf.to_csv(ofile, index=False)
nn_gdf.to_csv(ofile, index=False)



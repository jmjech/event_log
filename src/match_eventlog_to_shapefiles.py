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

def set_crs2_to_crs1(gdf1, gdf2):
    '''
    Set the CRS of the 2nd dataframe (gdf2) to the CRS of the 1st dataframe
    (gdf1) if they do not already match
    Input:
      gdf1: GeoPandas' dataframe
      gdf2: GeoPandas' dataframe
    Return:
      modified gdf2 if needed
    '''

    # check that both inputs are GeoPandas' dataframe
    if not isinstance(gdf1, gpd.GeoDataFrame):
        return None
    if not isinstance(gdf2, gpd.GeoDataFrame):
        return None

    # compare the CRS between the geodataframes
    if gdf2.crs != gdf1.crs:
      gdf2 = gdf2.to_crs(gdf1.crs)

    return gdf2


def get_crs_utm(gdf):
    '''
    Determine the CRS that will provide accurate spatial distances based on
    the longitude of the data. Use the GeoPandas' estimate_utm_crs() function
    Input:
      gdf: GeoPandas' dataframe
    Return:
      CRS object
    '''

    # check that the input is a GeoPandas' dataframe
    if not isinstance(gdf, gpd.GeoDataFrame):
        return None

    return gdf.estimate_utm_crs()


def create_columns_dictionary():
    '''
    Some of the BOEM shape files have similar field/column names but can have
    different information, more fields than we want to retain, or names
    that are confusing and ambiguous.
    The dictionary is structured as:
        key: code for the shapefile/data file
        value: sub-dictionary:
          key: original column name for those columns that we want to keep
          value: the new column name
    The sub-dictionary keys can be used as a list of columns to keep
    Input:
      none
    Return:
      dictionary
    '''

    # must have a "new" name as a value even if you are not renaming it. To
    # keep the same name use the original name
    column_dict = {'elog': 
                    { 'date_UTC': 'date_UTC',
                      'time_UTC': 'time_UTC',
                      'lat_dd': 'latitude_dd',
                      'lon_dd': 'longitude_dd',
                      'site_code': 'site_code',
                      'series_code': 'series_code',
                      'transect_code': 'transect_code',
                      'transect_number': 'transect_number',
                      'event_code': 'event_code',
                      'Comment': 'comment',
                      'gis_geometry': 'gis_geometry'
                    },
                  'boem_lease':
                    { 'LEASE_NUMB': 'boem_lease_code',
                      'LEASE_TYPE': 'boem_lease_type',
                      'RESOURCE': 'boem_lease_resource',
                      'COMPANY': 'boem_lease_company_name',
                      'ACRES': 'boem_lease_area_acres',
                      'STATE': 'boem_lease_state_name',
                      'PROTRACTIO': 'boem_lease_protraction_code',
                      'PROTRACT_1': 'boem_lease_protraction_name',
                      'PROJECT_NA': 'boem_lease_project_name',
                      'geometry': 'geometry'
                    },
                  'boem_div1':
                    { 'RGN_CODE': 'boem_div1_region_code',
                      'PROT_NUM': 'boem_div1_prot_num',
                      'PROT_NAME': 'boem_div1_prot_name',
                      'geometry': 'geometry'
                    },
                  'boem_div2':
                    { 'BLK_NUM': 'boem_div2_block_number',
                      'TOT_AREA': 'boem_div2_block_area',
                      'AREA_CODE': 'boem_div2_area_code',
                      'AC_LAB': 'boem_div2_areacode_label',
                      'geometry': 'geometry'
                    },
                  'boem_div3':
                    { 'BLK_NUM': 'boem_div3_block_number',
                      'ALQ_TOT_AR': 'boem_div3_aliquot_area',
                      'BLKLAB': 'boem_div3_block_label',
                      'ALQLAB': 'boem_div3_aliquot_code',
                      'geometry': 'geometry'
                    },
                  'boem_wtg':
                    { 'OBJECTID_1': 'boem_wtg_objectid_1',
                      'Constructi': 'boem_wtg_construction',
                      'Project': 'boem_wtg_project',
                      'Lease_Numb': 'boem_wtg_lease_numb',
                      'Wind_Turbi': 'boem_wtg_wind_turbine',
                      'x': 'boem_wtg_x',
                      'y': 'boem_wtg_y',
                      'geometry': 'geometry'
                    }
                }
    return column_dict


def keep_columns(gdf, gdf_code, cdict):
    '''
    Keep specified columns
    Input:
      gdf: the geo-dataframe
      gdf_code: the code for the gdf as defined by the top level code in 
                the columns dictionary
      columns_dict: the dictionary with the column names to keep
    Return:
      the modified geo-dataframe
    '''

    cols_to_keep = []
    [cols_to_keep.append(cname) for cname in cdict[gdf_code].keys()]
    return gdf[cols_to_keep].copy()


def rename_columns(gdf, gdf_code, cdict):
    '''
    Rename specified columns
    Input:
      gdf: the geo-dataframe
      gdf_code: the code for the gdf as defined by the top level code in 
                the columns dictionary
      columns_dict: the dictionary with the column names to rename
    Return:
      the modified geo-dataframe
    '''

    return gdf.rename(columns=cdict[gdf_code])


### main
# set parameter values
# set the EPSG values for the GeoPandas' dataframes
# EPSG=4326 will set the units to meters, which is used to calculate distances
pars_dict = { 'epsg_base': 4326 }
# maximum search distance in meters
pars_dict['max_distance'] = 2000
columns_dict = create_columns_dictionary()
col_names_to_keep = []

# read the data file
datafile = Path('/home/user/DX202301/event_log/DX202301_eventlog.csv')
elog_df = pd.read_csv(datafile)

# convert the event-log data to a geopandas dataframe
elog_df['gis_geometry'] = elog_df.apply(
        lambda row: Point(row['lon_dd'], row['lat_dd']), axis=1 )
elog_gdf = gpd.GeoDataFrame(elog_df, geometry='gis_geometry')
# set the base CRS
elog_gdf = elog_gdf.set_crs(epsg=pars_dict['epsg_base'], inplace=True)
# keep specified columns
elog_gdf = keep_columns(elog_gdf, 'elog', columns_dict)
# rename specified columns
elog_gdf = rename_columns(elog_gdf, 'elog', columns_dict)
# keep all the event-log columns
elog_cols_to_keep = elog_gdf.columns.tolist()
# the global set of column names
col_names_to_keep = elog_cols_to_keep

# Set the CRS to something that is specific to the area 
# where the data were collected. In the case of southern New England, we use
# EPSG = 32619 but make this generic to let the data determine the CRS
# this estimates UTM coordinates
pars_dict['crs_nn'] = elog_gdf.estimate_utm_crs()
pars_dict['epsg_nn'] = pars_dict['crs_nn'].to_epsg()

# set a UTM CRS for the event-log points
elog_gdf.to_crs(epsg=pars_dict['epsg_nn'], inplace=True)
# separate easting and northing from the geometry column
elog_gdf['easting'] = round(elog_gdf.geometry.x, 1)
elog_gdf['northing'] = round(elog_gdf.geometry.y, 1)

# read the wind lease outlines shapefile
shpfile = Path('/home/user/GIS/BOEM/Offshore_Wind_Lease_Outlines.shp')
lease_gdf = gpd.read_file(shpfile)
lease_gdf = keep_columns(lease_gdf, 'boem_lease', columns_dict)
lease_gdf = rename_columns(lease_gdf, 'boem_lease', columns_dict)
lease_gdf.to_crs(epsg=pars_dict['epsg_nn'], inplace=True)
# match the event-log points to the lease area polygons
# this retains all the event-log points even if they are not in a polygon
# points not in a polygon have NaN for the polygon data
matched_gdf = gpd.sjoin(elog_gdf, lease_gdf, 
                        how="left", predicate="within")
matched_gdf.set_geometry('gis_geometry')
matched_gdf = matched_gdf.drop(columns=['index_right'])

# read the OCS 1st Division polygons
#shpfile = Path('/home/user/GIS/BOEM/OCS_Block_Polygons_1st_Division.shp')
shpfile = Path('/home/user/GIS/BOEM/OCS_Protraction_Polygons_1st_Division_from-QGIS.shp')
div1_gdf = gpd.read_file(shpfile)
div1_gdf = keep_columns(div1_gdf, 'boem_div1', columns_dict)
div1_gdf = rename_columns(div1_gdf, 'boem_div1', columns_dict)
div1_gdf.to_crs(epsg=pars_dict['epsg_nn'], inplace=True)
matched_gdf = gpd.sjoin(matched_gdf, div1_gdf, 
                        how="left", predicate="within")
matched_gdf.set_geometry('gis_geometry')
matched_gdf = matched_gdf.drop(columns=['index_right'])

# read the OCS 2nd Division polygons
shpfile = Path('/home/user/GIS/BOEM/OCS_Block_Polygons_2nd_Division_Providence.shp')
div2_gdf = gpd.read_file(shpfile)
div2_gdf = keep_columns(div2_gdf, 'boem_div2', columns_dict)
div2_gdf = rename_columns(div2_gdf, 'boem_div2', columns_dict)
div2_gdf.to_crs(epsg=pars_dict['epsg_nn'], inplace=True)
matched_gdf = gpd.sjoin(matched_gdf, div2_gdf, 
                        how="left", predicate="within")
matched_gdf.set_geometry('gis_geometry')
matched_gdf = matched_gdf.drop(columns=['index_right'])

# read the OCS 3rd Division polygons
# geopandas is having trouble reading this file
#shpfile = Path('/home/user/GIS/BOEM/OCS_Aliquot_16ths_Polygons_-_3rd_Division.shp')
shpfile = Path('/home/user/GIS/BOEM/OCS_Aliquot_16ths_Polygons_-_3rd_Division_Providence-protraction.shp')
div3_gdf = gpd.read_file(shpfile)
div3_gdf = keep_columns(div3_gdf, 'boem_div3', columns_dict)
div3_gdf = rename_columns(div3_gdf, 'boem_div3', columns_dict)
div3_gdf.to_crs(epsg=pars_dict['epsg_nn'], inplace=True)
matched_gdf = gpd.sjoin(matched_gdf, div3_gdf, 
                        how="left", predicate="within")
matched_gdf.set_geometry('gis_geometry')
matched_gdf = matched_gdf.drop(columns=['index_right'])

# read the WTG shapefile
shpfile = Path('/home/user/GIS/BOEM/NOAA_Charts_WTG.shp')
wtg_gdf = gpd.read_file(shpfile)
wtg_gdf = keep_columns(wtg_gdf, 'boem_wtg', columns_dict)
wtg_gdf = rename_columns(wtg_gdf, 'boem_wtg', columns_dict)
wtg_gdf.to_crs(epsg=pars_dict['epsg_nn'], inplace=True)
# match the nearest turbine (WTG) to each point
nn_gdf = gpd.sjoin_nearest(matched_gdf, wtg_gdf, how='left', 
                           distance_col='distance_to_wtg',
                           max_distance=pars_dict['max_distance'])
# round the distances to one significant digit
nn_gdf['distance_to_wtg'] = round(nn_gdf['distance_to_wtg'], 1)
nn_gdf.drop(columns=['index_right'])

# output the new data file
ofile = Path('/home/user/DX202301/event_log/DX202301_eventlog_nn-BOEM.csv')
#nn_gdf.to_csv(ofile, index=False)


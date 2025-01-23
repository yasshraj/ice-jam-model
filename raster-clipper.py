import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.warp import reproject
from matplotlib import pyplot
import numpy as np

# Specify the input and output folder paths ---------------------------------------------------------------------------------
input_folder = '/Volumes/My Passport/Niab Files'
output_folder = '/Volumes/My Passport/Clipped Niab Files'

# read the basin shapefile --------------------------------------------------------------------------------------------------
basin_shapefile = gpd.read_file('/Users/ypurbey/Downloads/HW11_NiboraraRiver_stretch/HW11_Niborara_river_stretch.shp')

# loop through all files in the input folder and its subdirectories----------------------------------------------------------
for root, dirs, files in os.walk(input_folder):
    for filename in files:
        if filename.endswith('.TIF'):
            try:
                # Construct a full absolute file path to the currently working raster-------------------------------------------
                input_raster_path = os.path.join(root, filename)

                with rasterio.open(input_raster_path) as src:

                    # Reprojecting the basin shapefile to match the original raster's Coordinates-------------------------------
                    basin_shapefile_reprojected = basin_shapefile.to_crs(src.crs)

                    # Clipping the source raster using the reprojected basin shapefile------------------------------------------
                    clipped_raster, _ = mask(src, basin_shapefile_reprojected.geometry, crop=True)

                    # creating a new profile for the output raster matching all metadata of source------------------------------
                    profile = src.profile

                    # updating the profile to make sure the output raster will have same dimension as clipped----------------------
                    profile.update({
                        'height': clipped_raster.shape[1],
                        'width': clipped_raster.shape[2],
                        'transform': src.transform 
                    })

                    # Determine which subdirectory we are working on within the input folder---------------------------------------
                    relative_subdir = os.path.relpath(root, input_folder)

                    # Construct a full path to the output folder where we wanna save---------------------------------------------------
                    output_subfolder = os.path.join(output_folder, relative_subdir)

                    # making sure that the output folder exists; create it if not------------------------------------------------------
                    os.makedirs(output_subfolder, exist_ok=True)

                    # creating the output raster file fullpath within the output subfolder-------------------------------------------
                    output_raster_path = os.path.join(output_subfolder, f'clipped_{filename}')

                    # Create an output file and write the clipped data--------------------------------------------------------------
                    with rasterio.open(output_raster_path, 'w', **profile) as dst:
                        dst.write(clipped_raster)
                    
            except Exception as e:
                print(f"error occurred {filename}: {str(e)}")
                continue

import os
import numpy as np
import rasterio
import pandas as pd

# Define the directory where the clipped rasters and the existing csv file are located------------------------------------------
base_directory = '/Volumes/My Passport/Clipped Niab Files'
existing_data = pd.read_csv("/Volumes/My Passport/shape file/Lower Niobrara.csv")

# Define the threshold values for different indices------------------------------------------------------------------------------
thresholdNdsi = 0.21
thresholdSwi = 0.13
thresholdS3 = 0.14

thresholdNdwi = 0.17
thresholdMndwi = 0.14
thresholdAwei = 0.12

# Create a list to store data for each folder -------------------------------------------------------------------------------------
data = []

# Looping through all the subdirectories in the base directory folder --------------------------------------------------------------
for folder_name in os.listdir(base_directory):

    # Create a full path name of the given subdirectory ----------------------------------------------------------------------------
    folder_path = os.path.join(base_directory, folder_name)

    # Extract which landsat is used from the folder name ---------------------------------------------------------------------------
    satellite_name = folder_name.split('_')[0]

    # Check if the landsat name matches "LC09 or LC08" -----------------------------------------------------------------------------
    if satellite_name == "LC09" or satellite_name == "LC08":
        # if yes do following 
        # Extract the date from the folder name to match the date on csv file --------------------------------------------------------
        parts = folder_name.split('_')
        if len(parts) >= 4:
            date_part = parts[3]
            # Convert the date to the desired format (e.g., "12/24/21")
            year = date_part[:4]
            month = date_part[4:6]
            day = date_part[6:8]
            formatted_date = (f"{month}/{day}/{year}")

            # Initialize variables for each band -------------------------------------------------------------------------------------
            green, red, swir1, blue, nir, swir2 = None, None, None, None, None, None

            # Loop over the files in the current subdirectory and initialize bands ----------------------------------------------------
            for filename in os.listdir(folder_path):
                if filename.endswith('_B3.TIF'):
                    band3 = rasterio.open(os.path.join(folder_path, filename))
                    green = band3.read().astype('float')
                elif filename.endswith('_B4.TIF'):
                    band4 = rasterio.open(os.path.join(folder_path, filename))
                    red = band4.read().astype('float')
                elif filename.endswith('_B6.TIF'):
                    band6 = rasterio.open(os.path.join(folder_path, filename))
                    swir1 = band6.read().astype('float')
                elif filename.endswith('_B2.TIF'):
                    band2 = rasterio.open(os.path.join(folder_path, filename))
                    blue = band2.read().astype('float')
                elif filename.endswith('_B5.TIF'):
                    band5 = rasterio.open(os.path.join(folder_path, filename))
                    nir = band5.read().astype('float')
                elif filename.endswith('_B7.TIF'):
                    band7 = rasterio.open(os.path.join(folder_path, filename))
                    swir2 = band7.read().astype('float')

            # Calculate various indices -----------------------------------------------------------------------------------------------
            ndsi = np.where(
                (green + swir1) == 0.,
                0.,
                (green - swir1) / (green + swir1)
            )

            swi = np.where(
                (blue + nir) * (nir + swir1) == 0,
                0.,
                (blue * (nir - swir1)) / ((blue + nir) * (nir + swir1))
            )

            s3 = np.where(
                (nir + red) * (nir + swir1) == 0,
                0.,
                (green * (nir - swir1)) / ((nir + red) * (nir + swir1))
            )

            ndwi = np.where(
                (nir + swir1) == 0.,
                0.,
                (nir - swir1) / (nir + swir1)
            )

            mndwi = np.where(
                (green + swir1) == 0,
                0.,
                (green - swir1) / (green + swir1)
            )

            Awei = np.where(
                (blue + (2.5 * green) - 1.5 * (nir + swir1) - (0.25 * swir2)) > thresholdAwei,
                1,
                0
            )

            # masking out with the help of threshold values -----------------------------------------------------------------
            ndsi_mask = np.where(ndsi > thresholdNdsi, 1, 0)
            ndsi_mask = ndsi_mask.squeeze()
            swi_mask = np.where(swi > thresholdSwi, 1, 0)
            swi_mask = swi_mask.squeeze()
            s3_mask = np.where(s3 > thresholdS3, 1, 0)
            s3_mask = s3_mask.squeeze()
            ndwi_mask = np.where(ndwi > thresholdNdwi, 1, 0)
            ndwi_mask = ndwi_mask.squeeze()
            mndwi_mask = np.where(mndwi > thresholdMndwi, 1, 0)
            mndwi_mask = mndwi_mask.squeeze()
            Awei_mask = Awei.squeeze()

            # Count the number of ice and water pixels for each index --------------------------------------------------------------
            iceNdsi_pixels = np.count_nonzero(ndsi_mask)
            iceSwi_pixels = np.count_nonzero(swi_mask)
            iceS3_pixels = np.count_nonzero(s3_mask)
            waterNdwi_pixels = np.count_nonzero(ndwi_mask)
            waterMndwi_pixels = np.count_nonzero(mndwi_mask)
            waterAwei_pixels = np.count_nonzero(Awei_mask)

            # Calculate ice fractions for each index --------------------------------------------------------------------------------
            ice_fraction1 = iceNdsi_pixels / (waterNdwi_pixels + 1e-6)
            ice_fraction2 = iceSwi_pixels / (waterMndwi_pixels + 1e-6)
            ice_fraction3 = iceS3_pixels / (waterAwei_pixels + 1e-6)

            # print(ice_fraction1, ice_fraction2, ice_fraction3)

            # Append the data to the list using time as our key ---------------------------------------------------------------------
            data.append({
                "time": formatted_date,  
                "IceFraction1": ice_fraction1,
                "IceFraction2": ice_fraction2,
                "IceFraction3": ice_fraction3
            })

    # if the landsat name doesn't match "LC09 or LC08" do following ------------------------------------------------------------------------
    else:
        parts = folder_name.split('_')
        if len(parts) >= 4:
            date_part = parts[3]
            # Convert the date to the desired format (e.g., "12/24/21")-------------------------------------------------------------
            year = date_part[:4]
            month = date_part[4:6]
            day = date_part[6:8]
            formatted_date = (f"{month}/{day}/{year}")

            # Initialize variables for each band-------------------------------------------------------------------------------------
            green, red, swir1, blue, nir, swir2 = None, None, None, None, None, None

            for filename in os.listdir(folder_path):
                if filename.endswith('_B1.TIF'):
                    band1 = rasterio.open(os.path.join(folder_path, filename))
                    blue = band1.read().astype('float')
                if filename.endswith('_B2.TIF'):
                    band2 = rasterio.open(os.path.join(folder_path, filename))
                    green = band2.read().astype('float')
                elif filename.endswith('_B3.TIF'):
                    band3 = rasterio.open(os.path.join(folder_path, filename))
                    red = band3.read().astype('float')
                elif filename.endswith('_B5.TIF'):
                    band5 = rasterio.open(os.path.join(folder_path, filename))
                    swir1 = band5.read().astype('float')
                elif filename.endswith('_B4.TIF'):
                    band4 = rasterio.open(os.path.join(folder_path, filename))
                    nir = band4.read().astype('float')
                elif filename.endswith('_B7.TIF'):
                    band7 = rasterio.open(os.path.join(folder_path, filename))
                    swir2 = band7.read().astype('float')

            ndsi = np.where(
                (green + swir1) == 0.,
                0.,
                (green - swir1) / (green + swir1)
            )

            ndwi = np.where(
                (nir + swir1) == 0.,
                0.,
                (nir - swir1) / (nir + swir1)
            )

            ndsi_mask = np.where(ndsi > thresholdNdsi, 1, 0)
            ndsi_mask = ndsi_mask.squeeze()
            ndwi_mask = np.where(ndwi > thresholdNdwi, 1, 0)
            ndwi_mask = ndwi_mask.squeeze()

            iceNdsi_pixels = np.count_nonzero(ndsi_mask)
            waterNdwi_pixels = np.count_nonzero(ndwi_mask)

            ice_fraction1 = iceNdsi_pixels / (waterNdwi_pixels + 1e-6)

            data.append({
                "time": formatted_date,  
                "IceFraction1": ice_fraction1
            })


# Create a DataFrame from the data ----------------------------------------------------------------------------------------------
df = pd.DataFrame(data)

# Merge the existing data of csv with the new data based matching the "Time" column ------------------------------------------------
merged_data = existing_data.merge(df, on="time", how="left")

# Drop columns where all IceFraction1, IceFraction2, and IceFraction3 are NaN ---------------------------------------------------
merged_data.dropna(subset=['IceFraction1', 'IceFraction2', 'IceFraction3'], how='all', inplace=True)

# Fill NaN values with zeros (or any other desired value) -------------------------------------------------------------------------
merged_data.fillna(0, inplace=True)

# Save the merged DataFrame to a new CSV file --------------------------------------------------------------------------------------
merged_data.to_csv("/Volumes/My Passport/shape file/merged_ice_data1.csv", index=False)


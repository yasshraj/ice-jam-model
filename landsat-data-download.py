# Download Landsat 8 Images using Google Earth Engine
import ee
import geemap
ee.Initialize()

# Create a map object ---------------------------------------------------
Map = geemap.Map()

# Define the region of interest (roi) ------------------------------------
roi = ee.Geometry.Rectangle([73.0, 18.0, 80.0, 25.0])

# Load Landsat 8 image collection ----------------------------------------
image = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR") \
    .filterDate('2017-01-01', '2017-12-31') \
    .filterBounds(roi) \
    .sort('CLOUD_COVER') \
    .first()

# Define the visualization parameter for the Landsat 8 image -------------
visParamsTrue = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000, 'gamma': 1.4}
Map.addLayer(image, visParamsTrue, 'Landsat 2017')
Map.addLayer(image.clip(roi), visParamsTrue, 'Landsat 2017 SA')
Map.centerObject(roi, 10)

# Export to Drive --------------------------------------------------------
task = ee.batch.Export.image.toDrive(
    image=image.int16(),
    description='Landsat2017Chennai',
    scale=30,
    region=roi,
    maxPixels=1e13
)
task.start()
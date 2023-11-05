import subprocess
import numpy as np
from osgeo import gdal


def convert_band_m20_to_m10(m20, m10):
    image_band_conversion_cmd = [
        'gdalwarp',
        m20,
        m10,
        '-tr', '10', '10'
    ]
    subprocess.run(image_band_conversion_cmd)


def convert_band_m10_to_m20(m10, m20):
    image_band_conversion_cmd = [
        'gdalwarp',
        m10,
        m20,
        '-tr', '20', '20'
    ]
    subprocess.run(image_band_conversion_cmd)


def shift_raster(input_file, output_file, x_shift, y_shift):
    # Open the input raster file
    dataset = gdal.Open(input_file, gdal.GA_ReadOnly)

    # Get the geotransform
    geotransform = list(dataset.GetGeoTransform())

    # Modify the geotransform to apply the shift
    geotransform[0] += x_shift  # Shift in the east/west direction (longitude)
    geotransform[3] += y_shift  # Shift in the north/south direction (latitude)

    # Create the output raster file
    driver = gdal.GetDriverByName('GTiff')
    out_dataset = driver.Create(
        output_file,
        dataset.RasterXSize,
        dataset.RasterYSize,
        dataset.RasterCount,
        dataset.GetRasterBand(1).DataType
    )

    # Set the geotransform and projection on the output raster
    out_dataset.SetGeoTransform(tuple(geotransform))
    out_dataset.SetProjection(dataset.GetProjection())

    # Copy the data from the input raster to the output raster
    for i in range(1, dataset.RasterCount + 1):
        in_band = dataset.GetRasterBand(i)
        out_band = out_dataset.GetRasterBand(i)
        out_band.WriteArray(in_band.ReadAsArray())
        out_band.FlushCache()

    # Clean up
    dataset = None
    out_dataset = None


def calculate_ndbi_difference(new_images, old_images, output_image, gdal_calc_path):
    diff_calc_cmd = [
        'python',
        gdal_calc_path,
        '-a', old_images['08'],
        '-b', old_images['11'],
        '-c', new_images['08'],
        '-d', new_images['11'],
        '--outfile=' + output_image,
        '--calc="(b-a)/(b+a) - (d-c)/(d+c)"',
        '--overwrite'
        # '--NoDataValue=0'
    ]

    print("Running diff calc with the following files:")
    print(f'Old B08: {old_images["08"]}')
    print(f'Old B11: {old_images["11"]}')
    print(f'New B08: {new_images["08"]}')
    print(f'New B11: {new_images["11"]}')
    subprocess.run(diff_calc_cmd)


def calculate_ndwi(green_band_path, nir_band_path, output_ndwi_path, gdal_calc_path):
    # Use gdal_calc.py to calculate NDWI
    ndwi_calc_cmd = [
        'python',
        gdal_calc_path,
        '-A', green_band_path,
        '-B', nir_band_path,
        '--outfile=' + output_ndwi_path,
        '--calc="(A-B)/(A+B)"',
        '--NoDataValue=-9999'
    ]
    subprocess.run(ndwi_calc_cmd)


def create_water_mask(ndwi_path, water_mask_path, threshold=0.3):
    # Open the NDWI image
    ndwi_ds = gdal.Open(ndwi_path, gdal.GA_ReadOnly)
    ndwi_band = ndwi_ds.GetRasterBand(1)
    ndwi_array = ndwi_band.ReadAsArray()

    # Create a binary water mask
    water_mask = np.where(ndwi_array > threshold, 1, 0).astype(np.uint8)

    # Save the water mask to a new file
    driver = gdal.GetDriverByName('GTiff')
    water_mask_ds = driver.Create(water_mask_path, ndwi_ds.RasterXSize, ndwi_ds.RasterYSize, 1, gdal.GDT_Byte)
    water_mask_ds.GetRasterBand(1).WriteArray(water_mask)
    water_mask_ds.SetGeoTransform(ndwi_ds.GetGeoTransform())
    water_mask_ds.SetProjection(ndwi_ds.GetProjection())
    water_mask_ds = None  # Close the file


def apply_water_mask(image_path, water_mask_path, output_image_path):
    # Open the original image and the water mask
    image_ds = gdal.Open(image_path, gdal.GA_ReadOnly)
    water_mask_ds = gdal.Open(water_mask_path, gdal.GA_ReadOnly)

    # Read the image and mask arrays
    image_array = image_ds.GetRasterBand(1).ReadAsArray()
    water_mask_array = water_mask_ds.GetRasterBand(1).ReadAsArray()

    # Mask out water pixels
    image_array[water_mask_array == 1] = np.nan

    # Save the masked image to a new file
    driver = gdal.GetDriverByName('GTiff')
    output_ds = driver.Create(output_image_path, image_ds.RasterXSize, image_ds.RasterYSize, image_ds.RasterCount, image_ds.GetRasterBand(1).DataType)
    output_ds.GetRasterBand(1).WriteArray(image_array)
    output_ds.SetGeoTransform(image_ds.GetGeoTransform())
    output_ds.SetProjection(image_ds.GetProjection())
    output_ds = None  # Close the file
import subprocess
from osgeo import gdal
import os
import data_loader

# Settings
x_shift = 0
y_shift = 0

gdal_calc_path = 'C:\\ProgramData\\anaconda3\\Scripts\\gdal_calc.py'
output_image = data_loader.generate_output_image_name()

newimage_directory = "newimages/"
oldimage_directory = "oldimages/"
bands = ['08', '11']

def convert_band(m20_b11, m10_b11):
    image_band_conversion_cmd = [
        'gdalwarp',
        m20_b11,
        m10_b11,
        '-tr', '10', '10'
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


def process_images(new_images, old_images):
    for band in new_images:
        print("Converting band 11 to 10m resolution")
        if band == '11' and new_images[band].endswith('_20m.jp2'):
            new_converted = new_images[band].replace('.jp2', '_10m.jp2')
            old_converted = old_images[band].replace('.jp2', '_10m.jp2')
            convert_band(new_images[band], new_converted)
            convert_band(old_images[band], old_converted)
            new_images[band] = new_converted
            old_images[band] = old_converted

        # Shift rasters
        print(f'Shifting old rasters by X:{x_shift} and Y:{y_shift}')
        shifted_old = old_images[band].replace('.jp2', '_shifted.tif')
        shift_raster(old_images[band], shifted_old, x_shift, y_shift)

        # Update the dictionary with the shifted file paths
        old_images[band] = shifted_old

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

    print("Running diff calc")
    subprocess.run(diff_calc_cmd)


new_images = data_loader.find_band_files(newimage_directory, bands)
old_images = data_loader.find_band_files(oldimage_directory, bands)

process_images(new_images, old_images)
import subprocess
from osgeo import gdal
import os


newimage_directory = "newimage/"
oldimage_directory = "oldimage/"


def generate_output_image_name(base_name="output_image", extension=".tif"):
    counter = 1
    output_image = f"{base_name}_{counter}{extension}"

    while os.path.exists(output_image):
        counter += 1
        output_image = f"{base_name}_{counter}{extension}"

    return output_image


output_image = generate_output_image_name()
gdal_calc_path = 'C:\\ProgramData\\anaconda3\\Scripts\\gdal_calc.py'


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


x_shift = 0
y_shift = 0

#shift_raster(new_b08, shifted_new_b08, x_shift, y_shift)
shift_raster(old_b08, shifted_old_b08, x_shift, y_shift)
#shift_raster(converted_new_b11, shifted_new_b11, x_shift, y_shift)
shift_raster(converted_old_b11, shifted_old_b11, x_shift, y_shift)


def find_band_files(directory, bands):
    files = {band: None for band in bands}
    for filename in os.listdir(directory):
        for band in bands:
            if f"_B{band}_" in filename:
                files[band] = os.path.join(directory, filename)
                break  # Found the band file, move to the next one
    return files


def process_images(new_images, old_images):
    for band in new_images:
        if band == '11':
            new_converted = new_images[band].replace('.jp2', '_10m.jp2')
            old_converted = old_images[band].replace('.jp2', '_10m.jp2')
            convert_band(new_images[band], new_converted)
            convert_band(old_images[band], old_converted)
            new_images[band] = new_converted
            old_images[band] = old_converted

        # Shift rasters
        shifted_new = new_images[band].replace('.jp2', '_shifted.tif')
        shifted_old = old_images[band].replace('.jp2', '_shifted.tif')
        shift_raster(new_images[band], shifted_new, x_shift, y_shift)
        shift_raster(old_images[band], shifted_old, x_shift, y_shift)

        # Update the dictionary with the shifted file paths
        new_images[band] = shifted_new
        old_images[band] = shifted_old

    diff_calc_cmd = [
        'python',
        gdal_calc_path,
        '-a', shifted_old_b08,
        '-b', shifted_old_b11,
        '-c', new_images['08'],
        '-d', converted_new_b11,
        '--outfile=' + output_image,
        '--calc="(b-a)/(b+a) - (d-c)/(d+c)"',
        '--overwrite'
        # '--NoDataValue=0'
    ]

    print("Running diff calc")
    subprocess.run(diff_calc_cmd)

diff_calc_cmd = [
    'python',
    gdal_calc_path,
    '-a', shifted_old_b08,
    '-b', shifted_old_b11,
    '-c', new_b08,
    '-d', converted_new_b11,
    '--outfile=' + output_image,
    '--calc="(b-a)/(b+a) - (d-c)/(d+c)"',
    '--overwrite'
    #'--NoDataValue=0'
]

print("Running diff calc")
subprocess.run(diff_calc_cmd)


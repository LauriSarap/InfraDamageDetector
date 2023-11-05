import subprocess
from osgeo import gdal
import os
import data_loader
import utility_functions

# Settings
x_shift = -5
y_shift = -5
desired_resolution = f'10m'

gdal_calc_path = 'C:\\ProgramData\\anaconda3\\Scripts\\gdal_calc.py'
output_image = data_loader.generate_output_image_name(
    base_name=f'11_01_2023_and_27_09_2023_difference_{desired_resolution}')

newimage_directory = "new_images/"
oldimage_directory = "old_images/"
bands = ['08', '11']


def convert_bands(new_images, old_images, desired_resolution):
    if desired_resolution == '10m':
        print("Converting B11s to 10m resolution")
        if new_images['11'].endswith('_20m.jp2'):
            new_converted = new_images['11'].replace('_20m.jp2', '_10m.jp2')
            if os.path.exists(new_converted):
                print("New image already converted")
                new_images['11'] = new_converted
            else:
                utility_functions.convert_band_m20_to_m10(new_images['11'], new_converted)
                new_images['11'] = new_converted

        if old_images['11'].endswith('_20m.jp2'):
            old_converted = old_images['11'].replace('_20m.jp2', '_10m.jp2')
            if os.path.exists(old_converted):
                print("Old image already converted")
                old_images['11'] = old_converted
            else:
                utility_functions.convert_band_m20_to_m10(old_images['11'], old_converted)
                old_images['11'] = old_converted

    elif desired_resolution == '20m':
        print("Converting B08s to 20m resolution")
        if new_images['08'].endswith('_10m.jp2'):
            new_converted = new_images['08'].replace('_10m.jp2', '_20m.jp2')
            if os.path.exists(new_converted):
                print("New image already converted")
                new_images['08'] = new_converted
            else:
                utility_functions.convert_band_m10_to_m20(new_images['08'], new_converted)
                new_images['08'] = new_converted

        if old_images['08'].endswith('_10m.jp2'):
            old_converted = old_images['08'].replace('_10m.jp2', '_20m.jp2')
            if os.path.exists(old_converted):
                print("Old image already converted")
                old_images['08'] = old_converted
            else:
                utility_functions.convert_band_m10_to_m20(old_images['08'], old_converted)
                old_images['08'] = old_converted

    return new_images, old_images


def shift_old_rasters(old_images, x_shift, y_shift):
    print(f'Shifting old rasters by X:{x_shift} and Y:{y_shift}')
    for band in old_images:
        shifted_old = old_images[band].replace('.jp2', f'_shifted_{x_shift}x_{y_shift}y.jp2')
        if os.path.exists(shifted_old):
            print(f'{shifted_old} already shifted')
            old_images[band] = shifted_old
            continue
        else:
            utility_functions.shift_raster(old_images[band], shifted_old, x_shift, y_shift)
            old_images[band] = shifted_old

    return old_images


def calculate_difference(new_images, old_images, output_image):
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


new_images = data_loader.find_band_files(newimage_directory, bands, desired_resolution)
old_images = data_loader.find_band_files(oldimage_directory, bands, desired_resolution)

new_images, old_images = convert_bands(new_images, old_images, desired_resolution)
old_images = shift_old_rasters(old_images, x_shift, y_shift)
calculate_difference(new_images, old_images, output_image)
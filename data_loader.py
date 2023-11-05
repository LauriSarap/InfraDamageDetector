import os


def generate_output_image_name(base_name="output_image", extension=".tif"):
    counter = 1
    output_image = f"{base_name}_{counter}{extension}"

    while os.path.exists(output_image):
        counter += 1
        output_image = f"{base_name}_{counter}{extension}"

    return output_image


def find_band_files(directory, bands, resolution):
    files = {band: None for band in bands}

    # List all files in the directory
    all_files = os.listdir(directory)

    # Loop through each band and find the corresponding file
    for band in bands:
        print(f'Looking for band {band}')

        pattern = f"_B{band}_{resolution}.jp2"

        if band == '11' and resolution == '10m':
            pattern = "_B11_20m.jp2"

        if band == '08' and resolution == '20m':
            pattern = "_B08_10m.jp2"

        for filename in all_files:
            if pattern in filename:
                files[band] = os.path.join(directory, filename)
                print(f'Added {files[band]}')
                break

    return files

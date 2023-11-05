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

    if resolution == 'm10':
        for filename in os.listdir(directory):
            for band in bands:
                if f"_B{band}_{resolution}" in filename:
                    files[band] = os.path.join(directory, filename)
                    break
                elif f"_B_11_20m" in filename:
                    files[band] = os.path.join(directory, filename)
                    break

    if resolution == 'm20':
        for filename in os.listdir(directory):
            for band in bands:
                if f"_B{band}_{resolution}" in filename:
                    files[band] = os.path.join(directory, filename)
                    break
                elif f"_B_08_10m" in filename:
                    files[band] = os.path.join(directory, filename)
                    break
    return files

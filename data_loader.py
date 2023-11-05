import os


def generate_output_image_name(base_name="output_image", extension=".tif"):
    counter = 1
    output_image = f"{base_name}_{counter}{extension}"

    while os.path.exists(output_image):
        counter += 1
        output_image = f"{base_name}_{counter}{extension}"

    return output_image


def find_band_files(directory, bands):
    files = {band: None for band in bands}
    for filename in os.listdir(directory):
        for band in bands:
            if f"_B{band}_" in filename:
                files[band] = os.path.join(directory, filename)
                break  # Found the band file, move to the next one
    return files

import subprocess
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

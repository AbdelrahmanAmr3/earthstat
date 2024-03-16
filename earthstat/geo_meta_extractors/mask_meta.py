import rasterio
from pyproj import CRS


def maskSummary(raster_path):
    """
    This function takes a raster path as input and returns a dictionary containing the following information:

    - Mask_path: The path to the raster file
    - CRS: The coordinate reference system of the raster
    - Extent: The extent of the raster in the form of a tuple (min_x, min_y, max_x, max_y)
    - Data Type: The data type of the raster
    - NoData Value: The no data value of the raster
    - Spatial Resolution: The spatial resolution of the raster in the form of a tuple (width, height)
    - Pixel Size: The pixel size of the raster in the form of a tuple (x_size, y_size)
    - Min/Max Value: The minimum and maximum values of the raster
    """
    with rasterio.open(raster_path) as src:

        # Assuming there is a single band
        band_data = src.read(1, masked=True)

        # Compute minimum and maximum values
        min_value = band_data.min()
        max_value = band_data.max()
        crs = CRS(src.crs).name

        # Extracting essential information
        mask_summary = {
            "Mask_path": raster_path,
            "CRS": crs,
            "Extent": src.bounds,
            "Data Type": src.dtypes[0],
            "NoData Value": src.nodatavals[0],
            "Spatial Resolution": (src.width, src.height),
            "Pixel Size": src.res,
            "Min/Max Value": (min_value, max_value)
        }

        print("Mask Summary:\n")
        print('\n'.join(f"{key}: {value}" for key,
              value in mask_summary.items()))

        return mask_summary

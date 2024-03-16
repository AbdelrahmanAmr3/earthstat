import rasterio
from pyproj import CRS


def maskSummary(raster_path):
    """
    Generates a summary of essential information for a raster mask file.

    This function opens a raster file, reads its first band with masking enabled to handle nodata values, and then computes and extracts several key pieces of information about the raster. These include the coordinate reference system (CRS) name, geographical extent, data type of the raster, nodata value, spatial resolution, pixel size, and the minimum and maximum values within the raster.

    Parameters:
    - raster_path (str): The file path to the raster file.

    Returns:
    dict: A dictionary containing the mask path, CRS, geographical extent, data type, nodata value, spatial resolution (as width and height), pixel size, and the minimum and maximum value of the raster's first band.

    Example of use:
    >>> raster_summary = maskSummary('path/to/raster.tif')
    >>> print(raster_summary)
    {
        'Mask_path': 'path/to/raster.tif',
        'CRS': 'EPSG:4326',
        'Extent': BoundingBox(left=0.0, bottom=0.0, right=10.0, top=10.0),
        'Data Type': 'uint16',
        'NoData Value': -9999.0,
        'Spatial Resolution': (1024, 768),
        'Pixel Size': (0.1, 0.1),
        'Min/Max Value': (0, 255)
    }
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

import os
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from shapely.geometry import mapping
from tqdm import tqdm
from ..utils import savedFilePath


def clipRasterWithShapefile(raster_path, shapefile_path, invalid_values=None):
    """
    Clips a raster file using a shapefile, optionally filtering out specified invalid values.
    The clipped raster is saved in a new directory named 'clipped' plus the original file directory.

    Args:
        raster_path (str): Path to the raster file to be clipped.
        shapefile_path (str): Path to the shapefile used for clipping.
        invalid_values (list, optional): Values in the raster to treat as invalid and replace with NaN.

    The function creates a new directory (if it doesn't already exist) and saves the clipped raster there.
    """

    file_dir, file_name = savedFilePath(raster_path)

    global output_clip

    output_clip = 'clipped '+file_dir

    os.makedirs(output_clip, exist_ok=True)

    # Load the shapefile
    shapefile = gpd.read_file(shapefile_path)

    with rasterio.open(raster_path) as src:
        # Ensure the shapefile is in the same CRS as the raster
        shapefile = shapefile.to_crs(src.crs)

        # Clip the raster with the shapefile
        geoms = [mapping(shape) for shape in shapefile.geometry]
        out_image, out_transform = mask(src, geoms, crop=True)

        # Filter out invalid values
        if invalid_values:
            for invalid_value in invalid_values:
                out_image = np.where(
                    out_image == invalid_value, np.nan, out_image)

        out_meta = src.meta.copy()

    # Update metadata to reflect the number of layers, new transform, and new dimensions
    out_meta.update({
        "driver": "GTiff",
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform,
        # Ensure dtype is float to accommodate NaN values
        "dtype": 'float32'
    })

    output_path = os.path.join(
        output_clip, f"clipped_{file_name}")  # Modify as needed
    # Write the clipped and filtered raster to file
    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(out_image)


def clipMultipleRasters(raster_paths, shapefile_path, invalid_values=None):
    """
    Clips multiple raster files using a single shapefile, optionally filtering out specified invalid values.
    Each clipped raster is saved in a new directory named 'clipped' plus the original file directory.

    Args:
        raster_paths (list of str): Paths to the raster files to be clipped.
        shapefile_path (str): Path to the shapefile used for clipping.
        invalid_values (list, optional): Values in the raster to treat as invalid and replace with NaN.

    Returns:
        str: The path to the directory where clipped rasters are saved.

    Processes each raster sequentially, showing progress with a progress bar.
    """
    for raster_path in tqdm(raster_paths, total=len(raster_paths), desc="Clipping Rasters"):
        clipRasterWithShapefile(raster_path, shapefile_path, invalid_values)

    return output_clip

import os
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from shapely.geometry import mapping
from tqdm import tqdm
from ..utils import savedFilePath

from concurrent.futures import ProcessPoolExecutor


def clipRasterWithShapefile(raster_path, shapefile, invalid_values=None):
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
    file_dir, file_name = os.path.split(raster_path)

    output_clip = os.path.join(file_dir, 'clipped')

    with rasterio.open(raster_path) as src:
        geoms = [mapping(shape) for shape in shapefile.geometry]
        out_image, out_transform = mask(src, geoms, crop=True)
        if invalid_values:
            for invalid_value in invalid_values:
                out_image = np.where(
                    out_image == invalid_value, np.nan, out_image)

        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
            "dtype": 'float32',
            "compress": "lzw"
        })

    output_path = os.path.join(output_clip, f"clipped_{file_name}")
    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(out_image)


def clipMultipleRasters(raster_paths, shapefile_path, invalid_values=None):
    """
    Clips a raster file using a shapefile, optionally filtering out specified invalid values.
    The clipped raster is saved in a new directory named 'clipped' plus the original file directory.

    Args:
        raster_path (str): Path to the raster file to be clipped.
        shapefile_path (str): Path to the shapefile used for clipping.
        invalid_values (list, optional): Values in the raster to treat as invalid and replace with NaN.

    The function creates a new directory (if it doesn't already exist) and saves the clipped raster there.
    """

    # Enhancement: by open shapefile and create dir our of the loop
    output_clip_dir = os.path.join(os.path.dirname(raster_paths[0]), 'clipped')
    os.makedirs(output_clip_dir, exist_ok=True)

    shapefile = gpd.read_file(shapefile_path)

    # Using ProcessPoolExecutor to parallelize the task
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:

        # Use list to force execution and tqdm for progress bar
        list(tqdm(executor.map(clipRasterWithShapefile, raster_paths, [shapefile]*len(raster_paths), [invalid_values]*len(raster_paths)),
                  total=len(raster_paths), desc="Clipping Rasters"))

    return output_clip_dir

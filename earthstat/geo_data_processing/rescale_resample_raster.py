# Turn on/off resacle
# options to choose interpolation methond rather than bilinear interpolation

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio import warp
from ..utils import savedFilePath


def resamplingMethod(method):

    resampling_methods = {
        "bilinear": Resampling.bilinear,
        "nearest": Resampling.nearest,
        "average": Resampling.average,
        "cubic": Resampling.cubic,

    }

    return resampling_methods.get(method.lower(), Resampling.bilinear)


def rescaleResampleMask(mask_path, raster_data_path, scale_factor=None, resampling_method="bilinear"):
    """
    Rescales and resamples a mask raster based on a target raster's specifications. 
    Optionally applies scaling to the mask data's values and resamples using a specified method.

    Args:
        mask_path (str): Path to the mask raster file to be rescaled and resampled.
        raster_data_path (str): Path to the target raster file for matching specifications.
        scale_factor (tuple, optional): Min and max values for rescaling the mask data. Defaults to None.
        resampling_method (str, optional): Method for resampling ('bilinear', 'cubic', 'average', 'nearest'.). Defaults to bilinear.

    Returns:
        str: The path to the saved rescaled and resampled raster file.
    """
    file_dir, file_name = savedFilePath(mask_path)

    resampling_enum = resamplingMethod(resampling_method)

    with rasterio.open(raster_data_path) as target_raster:
        target_transform = target_raster.transform

    with rasterio.open(mask_path) as mask:
        mask_data = mask.read(1)

        if scale_factor:
            # Use actual min and max from the data
            old_min, old_max = mask_data.min(), mask_data.max()
            new_min, new_max = scale_factor
            rescaled_data = ((mask_data - old_min) /
                             (old_max - old_min)) * (new_max - new_min) + new_min
            print("\nRescaling Mask...")
            print("Resampling mask...")
        else:
            rescaled_data = mask_data  # Skip rescaling if scale_factor is None
            print("\nResampling mask...")
        out_meta = mask.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": target_raster.height,
            "width": target_raster.width,
            "transform": target_transform,
            "crs": target_raster.crs,
            "compress": "DEFLATE",  # Future Enhancement:specify best compression scheme here
            "predictor": "2",  # !!! good for continuous data !!!
            "zlevel": 1  # compression level, 9 is the highest
        })

    resampled_data = np.empty(
        shape=(target_raster.height, target_raster.width), dtype=out_meta['dtype'])
    warp.reproject(
        source=rescaled_data,
        destination=resampled_data,
        src_transform=mask.transform,
        src_crs=mask.crs,
        dst_transform=target_transform,
        dst_crs=target_raster.crs,
        resampling=resampling_enum
    )

    output_path = f'{file_dir}/rescaled_resampled_{resampling_method}_{file_name}'

    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(resampled_data, 1)

    print(f"Filtered shapefile saved to: {output_path}")

    return output_path

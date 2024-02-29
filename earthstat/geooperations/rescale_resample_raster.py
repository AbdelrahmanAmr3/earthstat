import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio import warp
from ..utils import savedFilePath


def rescaleResampleMask(mask_path, raster_data_path, scale_factor=(0, 100)):

    file_dir, file_name = savedFilePath(mask_path)

    with rasterio.open(raster_data_path) as target_raster:
        target_transform = target_raster.transform

    with rasterio.open(mask_path) as mask:
        mask_data = mask.read(1)
        old_min, old_max = 0, 10000
        new_min, new_max = scale_factor

        rescaled_data = ((mask_data - old_min) /
                         (old_max - old_min)) * (new_max - new_min) + new_min

        out_meta = mask.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": target_raster.height,
            "width": target_raster.width,
            "transform": target_transform,
            "crs": target_raster.crs,
            "compress": "DEFLATE",  # Specify compression scheme here
            "predictor": "2",  # Good for continuous data
            "zlevel": 1  # Compression level, 9 is the highest
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
        resampling=Resampling.bilinear
    )

    output_path = f'{file_dir}/rescaled_resampled_{file_name}'

    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(resampled_data, 1)

    return output_path

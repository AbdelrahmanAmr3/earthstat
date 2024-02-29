import rasterio
from rasterio.mask import mask
from rasterio import warp
from rasterio.enums import Resampling
from shapely.geometry import mapping
import numpy as np
import pandas as pd
from tqdm.auto import tqdm
import os
import geopandas as gpd


from ..utils import savedFilePath, extractDateFromFilename, loadTiff


def conAggregate(predictor_dir, shapefile_path, output_csv_path, crop_mask_path=None, use_crop_mask=False, predictor_name="Value"):
    predictor_pathes = loadTiff(predictor_dir)
    data_list = []
    shape_file = gpd.read_file(shapefile_path)

    if use_crop_mask:
        if crop_mask_path is None:
            raise ValueError(
                "Crop mask path must be provided if use_crop_mask is True.")
        mask_src = rasterio.open(crop_mask_path)
        # Dynamically read the no data value from the crop mask metadata
        no_data_value = mask_src.nodata

    for raster in tqdm(predictor_pathes, desc="Processing rasters", unit="raster"):
        file_name = os.path.basename(raster)
        date_str = extractDateFromFilename(file_name)

        with rasterio.open(raster) as src:
            for _, row in shape_file.iterrows():
                geom = row.geometry
                out_image, _ = mask(src, [geom], crop=True)

                if use_crop_mask:
                    mask_image, _ = mask(mask_src, [geom], crop=True)
                    if no_data_value is not None:
                        # Mask out no data values in the crop mask
                        valid_mask = (mask_image != no_data_value)
                    else:
                        # Assume all data is valid if no_data_value is not specified
                        valid_mask = np.ones_like(mask_image, dtype=bool)

                    valid_data = out_image[valid_mask]
                    valid_weights = mask_image[valid_mask]

                    if valid_weights.sum() > 0:  # Check to avoid division by zero
                        weighted_mean = np.nansum(
                            valid_data * valid_weights) / np.nansum(valid_weights)
                        # Round to 3 decimal places
                        value = np.round(weighted_mean, 3)
                    else:
                        value = np.nan  # No valid data points

                else:
                    # Round to 3 decimal places
                    value = np.round(np.nanmean(out_image), 3)

                new_row = {col: row[col]
                           for col in shape_file.columns if col != 'geometry'}
                new_row.update({
                    'date': date_str,
                    predictor_name: value
                })

                data_list.append(new_row)

    if use_crop_mask:
        mask_src.close()

    df = pd.DataFrame(data_list)
    df.to_csv(output_csv_path, index=False)

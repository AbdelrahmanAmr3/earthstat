import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import pandas as pd
import numpy as np
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from shapely.geometry import mapping

from ..utils import extractDateFromFilename, loadTiff


def process_and_aggregate_raster(raster, shapefile_path, use_crop_mask, crop_mask_path, invalid_values=None, no_data_value=None, predictor_name="Value"):
    """
    Process a single raster: clip with shapefile, then aggregate,
    and include data from each row in the shapefile in the output.
    """
    file_name = os.path.basename(raster)
    date_str = extractDateFromFilename(file_name)
    data_list = []

    shape_file = gpd.read_file(shapefile_path)

    with rasterio.open(raster) as src:
        shape_file_crs = shape_file.to_crs(src.crs)
        geoms = [mapping(shape) for shape in shape_file_crs.geometry]

        for index, geom in enumerate(geoms):
            geom_mask, geom_transform = mask(
                src, [geom], crop=True, all_touched=True)
            # Ensure data type consistency for NaN handling
            geom_mask = geom_mask.astype('float32')

            if invalid_values is not None:
                for invalid_value in invalid_values:
                    geom_mask[geom_mask == invalid_value] = np.nan

            if use_crop_mask and crop_mask_path:
                with rasterio.open(crop_mask_path) as mask_src:
                    crop_mask, _ = mask(
                        mask_src, [geom], crop=True, all_touched=True)
                if no_data_value is not None:
                    valid_mask = (crop_mask[0] != no_data_value)
                else:
                    valid_mask = np.ones_like(crop_mask[0], dtype=bool)

                valid_data = geom_mask[0][valid_mask]
                valid_weights = crop_mask[0][valid_mask]

                if valid_weights.sum() > 0:
                    weighted_mean = np.nansum(
                        valid_data * valid_weights) / np.nansum(valid_weights)
                else:
                    weighted_mean = np.nan
            else:
                valid_data = geom_mask[0][~np.isnan(geom_mask[0])]
                if valid_data.size > 0:
                    weighted_mean = np.nanmean(valid_data)
                else:
                    weighted_mean = np.nan

            # Create a new row with shapefile data and aggregated value
            row = shape_file.iloc[index]
            new_row = {col: row[col]
                       for col in shape_file.columns if col != 'geometry'}
            new_row.update({
                'date': date_str,
                predictor_name: np.round(weighted_mean, 3)
            })
            data_list.append(new_row)

    return data_list


def parallelAggregate(predictor_dir, shapefile_path, output_csv_path, crop_mask_path=None, use_crop_mask=False, invalid_values=None, predictor_name="Value"):
    predictor_paths = loadTiff(predictor_dir)
    data_list = []

    if use_crop_mask and not crop_mask_path:
        raise ValueError(
            "Crop mask path must be provided if use_crop_mask is true.")

    if use_crop_mask:
        mask_src = rasterio.open(crop_mask_path)
        no_data_value = mask_src.nodata
        mask_src.close()
    else:
        no_data_value = None

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_and_aggregate_raster, raster, shapefile_path, use_crop_mask,
                                   crop_mask_path, invalid_values, no_data_value, predictor_name) for raster in predictor_paths]

        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing rasters", unit="raster"):
            data_list.extend(future.result())

    df = pd.DataFrame(data_list)
    df.to_csv(output_csv_path, index=False)

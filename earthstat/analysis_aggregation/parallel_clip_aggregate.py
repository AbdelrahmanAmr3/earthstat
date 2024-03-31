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


def process_and_aggregate_raster(

        raster_path,
        shape_file,
        invalid_values=None,
        use_mask=False,
        mask_path=None,
        calculation_mode="overall_mean",
        predictor_name="Value",
        all_touched=False
):
    """
    Processes a single raster for aggregation into shapefile geometries.

    Args:
        raster_path (str): Path to the raster file.
        shape_file (GeoDataFrame): Loaded shapefile for geometries.
        invalid_values (list, optional): Values to consider as invalid in raster.
        use_mask (bool): If True, uses an additional mask for calculations.
        mask_path (str, optional): Path to the mask file, required if use_mask is True.
        calculation_mode (str): Mode of calculation ('overall_mean', 'weighted_mean', or 'filtered_mean').
        predictor_name (str): Column name for the output data.
        all_touched (bool): Consider all pixels that touch geometry for masking.

    Returns:
        list: Aggregated data for each geometry in the shapefile.
    """
    file_name = os.path.basename(raster_path)
    date_str = extractDateFromFilename(file_name)
    aggregated_data = []

    with rasterio.open(raster_path) as src:
        no_data_value = src.nodata
        geoms = [mapping(shape) for shape in shape_file.geometry]

        mask_no_data_value = None
        mask_src = None

        if use_mask and mask_path:
            mask_src = rasterio.open(mask_path)
            mask_no_data_value = mask_src.nodata

        for index, geom in enumerate(geoms):
            geom_mask, geom_transform = mask(
                src, [geom], crop=True, all_touched=all_touched)
            geom_mask = geom_mask.astype('float32')
            geom_mask[geom_mask == no_data_value] = np.nan

            if invalid_values:
                for invalid_value in invalid_values:
                    geom_mask[geom_mask == invalid_value] = np.nan

            if use_mask and mask_path and mask_src:
                crop_mask, _ = mask(
                    mask_src, [geom], crop=True, all_touched=all_touched)

                if calculation_mode == "weighted_mean":
                    valid_mask = (crop_mask[0] != mask_no_data_value)
                    valid_data = geom_mask[0][valid_mask]
                    valid_weights = crop_mask[0][valid_mask]
                    mean_value = np.nansum(valid_data * valid_weights) / np.nansum(
                        valid_weights) if np.nansum(valid_weights) > 0 else np.nan

                elif calculation_mode == "filtered_mean":
                    valid_mask = (crop_mask[0] != mask_no_data_value)
                    masked_data = geom_mask[0][valid_mask]
                    mean_value = np.nanmean(masked_data) if np.nansum(
                        masked_data) > 0 else np.nan

            elif calculation_mode == "overall_mean" or not use_mask:
                mean_value = np.nanmean(geom_mask)

            new_row = {col: shape_file.iloc[index][col]
                       for col in shape_file.columns if col != 'geometry'}
            new_row.update({'date': date_str, predictor_name: mean_value})
            aggregated_data.append(new_row)

        if mask_src:
            mask_src.close()

    return aggregated_data


def parallelAggregate(

    predictor_dir,
    shapefile_path,
    output_csv_path,
    mask_path=None,
    use_mask=False,
    invalid_values=None,
    calculation_mode="overall_mean",
    predictor_name="Value",
    all_touched=False,
    max_workers=None

):
    """
    Aggregates raster data from a directory in parallel into shapefile geometries, optionally using a mask.

    Args:
        predictor_dir (str): Directory containing raster datasets.
        shapefile_path (str): Path to the shapefile.
        output_csv_path (str): Path to save the aggregated CSV.
        mask_path (str, optional): Path to the mask file, required if use_mask is True.
        use_mask (bool): Use a mask for the aggregation process.
        invalid_values (list, optional): List of values to treat as invalid in the raster data.
        calculation_mode (str): Determines how values are aggregated ('overall_mean', 'weighted_mean', or 'filtered_mean').
        predictor_name (str): Name for the output predictor column.
        all_touched (bool): Include all pixels touching geometry in the aggregation.

    Raises:
        ValueError: If use_mask is True and mask_path is not provided.

    Returns a CSV with aggregated data per shapefile geometry. Utilizes multiprocessing for efficiency.
    """

    if not max_workers:
        max_workers = os.cpu_count() - 1 if os.cpu_count() > 1 else 1

    predictor_paths = loadTiff(predictor_dir)
    data_list = []

    shape_file = gpd.read_file(shapefile_path)

    if use_mask and not mask_path:
        raise ValueError("Mask path must be provided if use_mask is True.")

    with ProcessPoolExecutor(max_workers=max_workers) as executor:

        futures = [

            executor.submit(

                process_and_aggregate_raster,
                raster_path,
                shape_file,
                invalid_values,
                use_mask,
                mask_path,
                calculation_mode,
                predictor_name,
                all_touched

            ) for raster_path in predictor_paths
        ]

        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing rasters", unit="raster"):
            data_list.extend(future.result())

    df = pd.DataFrame(data_list)
    df[predictor_name] = df[predictor_name].round(3)
    df.to_csv(output_csv_path, index=False)

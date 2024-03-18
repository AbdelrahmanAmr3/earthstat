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


from ..utils import extractDateFromFilename, loadTiff


def process_and_aggregate_raster(raster_path, shape_file, invalid_values=None, use_mask=False, mask_path=None, calculation_mode="overall_mean", predictor_name="Value", all_touched=False):
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


def conAggregate(predictor_dir, shapefile_path, output_csv_path, mask_path=None, use_mask=False, invalid_values=None, calculation_mode="overall_mean", predictor_name="Value", all_touched=False):

    predictor_paths = loadTiff(predictor_dir)
    data_list = []

    shape_file = gpd.read_file(shapefile_path)

    if use_mask and not mask_path:
        raise ValueError("Mask path must be provided if use_mask is True.")

    for raster_path in tqdm(predictor_paths, desc="Processing rasters", unit="raster"):
        # Directly call the processing function for each raster
        data = process_and_aggregate_raster(raster_path, shape_file, invalid_values,
                                            use_mask, mask_path, calculation_mode, predictor_name, all_touched)
        data_list.extend(data)

    df = pd.DataFrame(data_list)
    df[predictor_name] = df[predictor_name].round(3)
    df.to_csv(output_csv_path, index=False)


# def Aggregate(predictor_dir, shapefile_path, output_csv_path, crop_mask_path=None, use_crop_mask=False, predictor_name="Value"):

#     predictor_pathes = loadTiff(predictor_dir)
#     data_list = []
#     shape_file = gpd.read_file(shapefile_path)

#     if use_crop_mask:
#         if crop_mask_path is None:
#             raise ValueError(
#                 "Crop mask path must be provided if use_crop_mask is True.")
#         mask_src = rasterio.open(crop_mask_path)
#         # Dynamically read the no data value from the crop mask metadata
#         no_data_value = mask_src.nodata

#     for raster in tqdm(predictor_pathes, desc="Processing rasters", unit="raster"):
#         file_name = os.path.basename(raster)
#         date_str = extractDateFromFilename(file_name)

#         with rasterio.open(raster) as src:
#             for _, row in shape_file.iterrows():
#                 geom = row.geometry
#                 out_image, _ = mask(src, [geom], crop=True)

#                 if use_crop_mask:
#                     mask_image, _ = mask(mask_src, [geom], crop=True)
#                     if no_data_value is not None:
#                         # Mask out no data values in the crop mask
#                         valid_mask = (mask_image != no_data_value)
#                     else:
#                         # Assume all data is valid if no_data_value is not specified
#                         valid_mask = np.ones_like(mask_image, dtype=bool)

#                     valid_data = out_image[valid_mask]
#                     valid_weights = mask_image[valid_mask]

#                     if valid_weights.sum() > 0:  # Check to avoid division by zero
#                         weighted_mean = np.nansum(
#                             valid_data * valid_weights) / np.nansum(valid_weights)
#                         # Round to 3 decimal places
#                         value = np.round(weighted_mean, 3)
#                     else:
#                         value = np.nan  # No valid data points

#                 else:
#                     # Round to 3 decimal places
#                     value = np.round(np.nanmean(out_image), 3)

#                 new_row = {col: row[col]
#                            for col in shape_file.columns if col != 'geometry'}
#                 new_row.update({
#                     'date': date_str,
#                     predictor_name: value
#                 })

#                 data_list.append(new_row)

#     if use_crop_mask:
#         mask_src.close()

#     df = pd.DataFrame(data_list)
#     df.to_csv(output_csv_path, index=False)


# def conAggregate():
#     """
#     Aggregates raster values to polygons in a shapefile, optionally using a crop mask for weighted calculations.

#     Args:
#         predictor_dir (str): Directory containing raster datasets.
#         shapefile_path (str): Path to the shapefile with polygons for aggregation.
#         output_csv_path (str): Path where the aggregated output CSV will be saved.
#         crop_mask_path (str, optional): Path to the crop mask raster, required if use_crop_mask is True.
#         use_crop_mask (bool): Whether to use the crop mask for weighted aggregation.
#         predictor_name (str): Column name for the aggregated values in the output CSV.

#     Raises:
#         ValueError: If use_crop_mask is True but crop_mask_path is not provided.

#     Aggregates values from each raster within the specified directory to each polygon in the shapefile,
#     writing the results to a CSV file. If a crop mask is used, values are aggregated using weights from
#     the mask; otherwise, simple averaging is applied.
#     """

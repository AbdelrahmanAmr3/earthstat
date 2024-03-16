from ..geo_data_processing.rescale_resample_raster import rescaleResampleMask
from ..geo_data_processing.shapefile_process import reprojectShapefileToRaster


def processCompatibilityIssues(actions, mask_path, predictor_data_path, shapefile_path, rescale_factor=None, resampling_method="bilinear"):
    """
    Processes identified compatibility issues by resampling masks and/or reprojection of shapefiles
    to match a predictor dataset's specifications.

    Args:
        actions (dict): A dictionary indicating which compatibility actions are required.
        mask_path (str): Path to the original mask file.
        predictor_data_path (str): Path to the raster dataset used as the predictor.
        shapefile_path (str): Path to the original shapefile.
        rescale_factor (tuple, optional): Min and max values for rescaling the mask data.
        resampling_method (str): Method to use for resampling ('bilinear' by default).

    Returns:
        dict: Updated paths for the processed mask and shapefile.

    Performs resampling of the mask and reprojection of the shapefile based on the actions specified
    in the `actions` dictionary. Returns updated file paths for these processed files.
    """
    updated_paths = {
        'crop_mask': mask_path,
        'shapefile': shapefile_path
    }

    if not actions['is_compatible']:
        if actions['resample_mask']:
            updated_paths['crop_mask'] = rescaleResampleMask(mask_path,
                                                             predictor_data_path,
                                                             scale_factor=rescale_factor,
                                                             resampling_method=resampling_method)

        if actions['reproject_shapefile']:
            print("\nReprojecting shapefile...")
            updated_paths['shapefile'] = reprojectShapefileToRaster(
                predictor_data_path, shapefile_path)

    else:
        print("No compatibility issues detected. Proceeding without resampling or reprojection.")

    return updated_paths

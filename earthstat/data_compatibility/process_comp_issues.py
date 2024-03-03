from ..geo_data_processing.rescale_resample_raster import rescaleResampleMask
from ..geo_data_processing.shapefile_process import reprojectShapefileToRaster


def processCompatibilityIssues(actions, mask_path, predictor_data_path, shapefile_path, rescale_factor=(0, 100),resampling_method="bilinear"):

    updated_paths = {
        'crop_mask': mask_path,
        'shapefile': shapefile_path
    }

    if not actions['is_compatible']:
        if actions['resample_mask']:
            print("\nResampling mask...")
            updated_paths['crop_mask'] = rescaleResampleMask(mask_path,
                                                             predictor_data_path,
                                                             scale_factor=rescale_factor,
                                                             resampling_method)

        if actions['reproject_shapefile']:
            print("Reprojecting shapefile...")
            reprojectShapefileToRaster(shapefile_path,
                                       predictor_data_path,
                                       output_shapefile_path=output_reprojected_shapefile_path)
            updated_paths['shapefile'] = output_reprojected_shapefile_path

    else:
        print("No compatibility issues detected. Proceeding without resampling or reprojection.")

    return updated_paths
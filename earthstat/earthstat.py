from .geo_meta_extractors.predictor_meta import predictorMeta
from .data_converter.netcdf_to_tiff import convertToTIFF
from .geo_meta_extractors.mask_meta import maskSummary
from .geo_meta_extractors.shapefile_meta import shapefileMeta
from .data_compatibility.data_compatibility import checkDataCompatibility
from .data_compatibility.process_comp_issues import processCompatibilityIssues
from .geo_data_processing.shapefile_process import filterShapefile as extractROI
from .geo_data_processing.clip_raster import clipMultipleRasters as clipRaster
from .analysis_aggregation.aggregate_process import conAggregate
from .analysis_aggregation.parallel_clip_aggregate import parallelAggregate
from .utils import loadTiff

import os
from datetime import datetime


class EarthStat():

    def __init__(self, predictor_name):

        self.predictor_name = predictor_name
        self.predictor_paths = None
        self.predictor_example = None
        self.mask_path = None
        self.shapefile_path = None
        self.process_compatibility = None
        self.use_crop_mask = True  # IMPROVE: We have to change it relate the user

        # Meta Data
        self.predictory_meta = None
        self.mask_meta = None
        self.shapefile_meta = None

        # Modified Data
        self.ROI = None
        self.clipped_dir = None

        # Aggregated Data path
        self.aggregated_csv = None

    def initDataDir(self, data_dir):

        has_tiff = any(file.endswith('.tif') for file in os.listdir(data_dir))

        if has_tiff:
            print("TIFF data found. Loading...\n")
            # Proceed to load TIFF data without conversion
            self.predictor_paths = loadTiff(data_dir)
        else:
            # If no TIFF files, check for netCDF files
            has_netcdf = any(file.endswith('.nc')
                             for file in os.listdir(data_dir))

            if has_netcdf:
                convert_choice = input(
                    "The data is in netCDF format. Do you want to convert it to TIFF? (y/n): ")

                if convert_choice.lower() == 'y':
                    # If user chooses to convert, convert the data to TIFF
                    data_dir = convertToTIFF(data_dir)
                    print("Data converted to TIFF successfully.\n")
                    self.predictor_paths = loadTiff(data_dir)
                else:

                    print(
                        "Data will not be converted. EarthStat just works with TIFF data.")
                    return
            else:
                print("No netCDF or TIFF data found in the directory.")
                return

        # Common steps to process loaded TIFF data
        self.predictor_example = self.predictor_paths[0]
        self.predictory_meta = predictorMeta(data_dir, self.predictor_name)
        print("\nPredictor Paths Initialized Correctly, Initialize The Mask's Path")

    def initMaskPath(self, mask_path):
        self.mask_path = mask_path
        # Function to identify mask information
        self.mask_meta = maskSummary(self.mask_path)
        print("\nMask Initialized Correctly, Initialize The Shapefile")

    def initShapefilePath(self, shapefile_path):
        self.shapefile_path = shapefile_path
        self.shapefile_meta = shapefileMeta(self.shapefile_path)

        if self.mask_path and self.predictor_paths:
            print(
                "\nShapefile Initialized Correctly, You Can Check The Data Compatibility")
        else:
            print(
                "\nShapefile Initialized Correctly, But The Mask or Predictor Paths are not initialized")

    def DataCompatibility(self):
        compatibility_result = checkDataCompatibility(
            self.predictor_example, self.mask_path, self.shapefile_path)
        self.process_compatibility = compatibility_result
        if self.process_compatibility['is_compatible']:
            print("\nCOMPATIBILITY CHECK PASSED: The data is compatible. No resolution or projection mismatches were detected.")
        else:
            print(
                "\nCOMPATIBILITY ISSUE DETECTED: The data is not compatible based on the current checks.")

    def fixCompatibilityIssues(self, rescale_factor=None, resampling_method="bilinear"):
        print("Checking for compatibility issues...")

        if not self.process_compatibility['is_compatible']:
            print("Compatibility issues detected. Starting the fix process...")

            if self.process_compatibility['resample_mask']:
                print(
                    "- Resampling the mask to match the raster's resolution and extent.")
            else:
                print("- The mask does not require resampling.")

            if self.process_compatibility['reproject_shapefile']:
                print(
                    "- Reprojecting the shapefile to match the raster's coordinate reference system.")
            else:
                print("- The shapefile does not require reprojection.")

            updated_paths = processCompatibilityIssues(
                self.process_compatibility, self.mask_path, self.predictor_example, self.shapefile_path, rescale_factor, resampling_method)

            self.mask_path = updated_paths.get('crop_mask', self.mask_path)
            self.shapefile_path = updated_paths.get(
                'shapefile', self.shapefile_path)

            if self.process_compatibility['resample_mask']:
                print(
                    f"Mask resampled successfully. Updated mask path: [{self.mask_path}]")

            print("\nRe-checking data compatibility after applying fixes...\n")

            self.process_compatibility = checkDataCompatibility(
                self.predictor_example, self.mask_path, self.shapefile_path)

            if self.process_compatibility['is_compatible']:
                print(
                    "\nAll compatibility issues have been resolved. Data is now compatible.")
            else:
                print(
                    "Some compatibility issues could not be resolved automatically. Further manual intervention required.")
        else:
            print(
                "No compatibility issues detected. Predictor, mask, and shapefile are already compatible.")

    def selectRegionOfInterest(self, countries, country_column_name):

        self.ROI = extractROI(self.shapefile_path,
                              countries, country_column_name)

        if self.ROI:
            print(
                f"Region of Interest (ROI) successfully selected based on the specified countries: {', '.join(countries)}.")
        else:
            print("Failed to select the Region of Interest (ROI). Please check the country names and column name provided.")

    def clipPredictor(self, invalid_values=None):
        print("Clipping the predictor data...")
        if self.ROI:
            self.clipped_dir = clipRaster(
                self.predictor_paths, self.ROI, invalid_values=invalid_values)
            print("Clipping operation successful with the Region of Interest (ROI).")

        elif not self.ROI:
            self.clipped_dir = clipRaster(
                self.predictor_paths, self.shapefile_path, invalid_values=invalid_values)
            print("Clipping operation successful with the main shapefile.")

        else:
            print(
                "Failed to clip the predictor data. Check the shapefile and predictor paths")

    def runAggregation(self):
        print("Starting aggregation...")
        aggregate_output = f'Aggregated_{self.predictor_name}.csv'

        # Check if a Region of Interest (ROI) has been selected for aggregation
        if self.ROI:
            print(
                f"Starting aggregation with the selected Region of Interest (ROI) for {self.predictor_name}.")
            self.aggregated_csv = conAggregate(self.clipped_dir, self.ROI, aggregate_output, self.mask_path,
                                               use_crop_mask=self.use_crop_mask, predictor_name=self.predictor_name)

        else:
            print(
                f"Starting aggregation with the original shapefile for {self.predictor_name}.")
            self.aggregated_csv = conAggregate(self.clipped_dir,
                                               self.shapefile_path,
                                               aggregate_output,
                                               self.mask_path,
                                               use_crop_mask=self.use_crop_mask,
                                               predictor_name=self.predictor_name)

        print(f"Aggregation complete. Data saved to {aggregate_output}.")

    def runParallelAggregation(self, use_mask=False, invalid_values=None, calculation_mode="overall_mean", all_touched=False):
        print("Starting aggregation...")

        self.use_mask = use_mask
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        aggregate_output = f'Aggregated_{calculation_mode}_{self.predictor_name}_{timestamp}.csv'

        # Check if a Region of Interest (ROI) has been selected for aggregation
        if self.ROI:
            print(
                f"Starting aggregation with the selected Region of Interest (ROI) for {self.predictor_name}.")
            self.aggregated_csv = parallelAggregate(self.predictor_dir, self.ROI, aggregate_output, self.mask_path,
                                                    use_mask, invalid_values, calculation_mode, predictor_name=self.predictor_name, all_touched=all_touched)

        else:
            print(
                f"Starting aggregation with the original shapefile for {self.predictor_name}.")
            self.aggregated_csv = parallelAggregate(self.predictor_dir,
                                                    self.shapefile_path,
                                                    aggregate_output,
                                                    self.mask_path,
                                                    use_mask=self.use_mask,
                                                    predictor_name=self.predictor_name)

        print(f"Aggregation complete. Data saved to {aggregate_output}.")

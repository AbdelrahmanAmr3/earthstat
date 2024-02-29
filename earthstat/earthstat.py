from .data_processing.data_loader import loadData
from .data_processing.data_compatibility import checkDataCompatibility
from .analysis_aggregation.process_comp_issues import processCompatibilityIssues
from .geooperations.shapefile_process import filterShapefile as extractROI
from .geooperations.clip_raster import clipMultipleRasters as clipRaster
from .analysis_aggregation.aggregate_process import conAggregate


class EarthStat():

    def __init__(self, predictor_name):
        self.predictor_name = predictor_name
        self.predictor_pathes = None
        self.predictor_example = None
        self.mask_path = None
        self.shapefile_path = None
        self.process_compatibility = None
        self.use_crop_mask = True  # IMPROVE: We have to change it relate the user

        # Modified Data
        self.ROI = None
        self.clipped_dir = None

        # Aggregated Data path
        self.aggregated_csv = None

    def initDataDir(self, path):

        loaded_paths = loadData(path, self.predictor_name)

        self.predictor_pathes = loaded_paths
        self.predictor_example = self.predictor_pathes[0]

        print("\nPredictor Initialized Correctly, Initialize The Mask")

    def initMask(self, mask_path):
        self.mask_path = mask_path
        print("Mask Initialized Correctly, Initialize The Shapefile")

    def initShapefile(self, shapefile_path):
        self.shapefile_path = shapefile_path
        print("Shapefile Initialized Correctly, Now Check The Data Compatibility")

    def DataCompatibility(self):
        compatibility_result = checkDataCompatibility(
            self.predictor_example, self.mask_path, self.shapefile_path)
        self.process_compatibility = compatibility_result
        if self.process_compatibility['is_compatible']:
            print("\nCOMPATIBILITY CHECK PASSED: The data is compatible. No resolution or projection mismatches were detected.")
        else:
            print(
                "\nCOMPATIBILITY ISSUE DETECTED: The data is not compatible based on the current checks.")

    def fixCompatibilityIssues(self):
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
                self.process_compatibility, self.mask_path, self.predictor_example, self.shapefile_path)

            self.mask_path = updated_paths.get('crop_mask', self.mask_path)
            self.shapefile_path = updated_paths.get(
                'shapefile', self.shapefile_path)

            if self.process_compatibility['resample_mask']:
                print(
                    f"Mask resampled successfully. Updated mask path: [{self.mask_path}]")
            if self.process_compatibility['reproject_shapefile']:
                print(
                    f"Shapefile reprojected successfully. Updated shapefile path: [{self.shapefile_path}]")

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

    def clipPredictor(self, invalid_values):

        self.clipped_dir = clipRaster(
            self.predictor_pathes, self.ROI, invalid_values=invalid_values)
        if self.clipped_dir:
            print(
                f"Clipping operation successful. Clipped data stored in: {self.clipped_dir}")

        else:
            print(
                "Failed to clip the predictor data. Please check the input paths and parameters.")

    def runAggregation(self):
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

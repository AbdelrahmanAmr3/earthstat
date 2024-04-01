# xEarthStat's submodules
from .xES.xES_utiles import create_directories, extract_AgERA5_zips
from .xES.download_AgERA5py import AgERA5Downloader
from .xES.DekadalDatasetBuilder import DekadalDatasetBuilder
from .xES.DailyDatasetBuilder import DailyDatasetBuilder
from .xES.get_csv import get_merged_csv

# Python built-in Libraries
import os
import geopandas as gpd


class xEarthStat():
    """
    xEarthStat is a Python package that provides a simple interface to download and aggregate AgERA5 data for a given region of interest (ROI).
    """

    def __init__(self):

        self.area_name = None
        self.shapefile = None
        self.aggregation_workflow = None
        self.processing = None
    # create directories for xEarthStat workflow

    def init_workflow(self, area_name, shapefile_path=None):

        self.area_name = area_name  # Essential for creating directories
        os.makedirs(self.area_name, exist_ok=True)

        if shapefile_path:
            self.shapefile = gpd.read_file(shapefile_path)
            # make sure the shapefile with wg84 projection
            self.shapefile = self.shapefile.to_crs(epsg=4326)

        else:
            print("No Shapefile Provided. You can download data without aggregation.")
            print(
                "If you plan to aggregate the data later, you will be asked to provide the shapefile path.")
            self.shapefile = None

    def init_AgERA5_downloader(self, parameters, bounding_box, start_year, end_year):

        self.data_downloader = AgERA5Downloader(

            self.area_name,
            parameters,
            bounding_box,
            start_year,
            end_year
        )

    def download_AgERA5(self, num_requests, extract=True):

        self.data_downloader.download_AgERA5(num_requests)
        # ask users if they want to extract the data
        if extract:
            create_directories(self.area_name)
            extract_AgERA5_zips(self.area_name)
            print("AgERA5 Data Downloaded and Extracted Successfully")

    # for extract later

    def extract_AgERA5(self):
        create_directories(self.area_name)
        extract_AgERA5_zips(self.area_name)
        print("AgERA5 Data Extracted Successfully")

    def Aggregate_AgERA5(
            self, dataset_type='dekadal', all_touched=False, stat='mean',
            multi_processing=False, max_workers=os.cpu_count()):

        self._check_shapefile()

        self.aggregation_workflow = dataset_type
        self.processing = multi_processing

        self._init_aggregation_workflow(
            self.aggregation_workflow, all_touched=all_touched, stat=stat)

        print(f"Building {self.aggregation_workflow} ({stat}) Datasets...")
        self.dataset_builder.build_datasets(max_workers=max_workers)
        print(f"{self.aggregation_workflow} Datasets Aggregated Successfully")

    def _init_aggregation_workflow(
            self, dataset_type, max_workers=os.cpu_count(),
            all_touched=False, stat='mean'):

        if dataset_type == 'dekadal':

            self.dataset_builder = DekadalDatasetBuilder(

                self.area_name,
                self.shapefile,
                multiprocessing=self.processing,
                max_workers=max_workers,
                all_touched=all_touched,
                stat=stat

            )

        else:

            self.dataset_builder = DailyDatasetBuilder(

                self.area_name,
                self.shapefile,
                multiprocessing=self.processing,
                max_workers=max_workers,
                all_touched=all_touched,
                stat=stat

            )

    def AgERA5_merged_csv(self, kelvin_to_celsius=False, output_name=None):
        get_merged_csv(self.area_name, self.aggregation_workflow,
                       kelvin_to_celsius=kelvin_to_celsius, output_name=output_name)
        print("CSV Merged Successfully")

    def _check_shapefile(self):
        if not self.shapefile:

            print("Shapefile not provided")

            shapefile_path = input(
                "Please provide the path to the shapefile: ")

            self.shapefile = gpd.read_file(shapefile_path)
            self.shapefile = self.shapefile.to_crs(epsg=4326)
            print("Shapefile Loaded Successfully\n")

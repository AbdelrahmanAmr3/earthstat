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

    def __init__(self, area_name, shapefile_path, workflow='daily', multi_processing=False):

        self.area_name = area_name  # create directories
        self.workflow = workflow
        self.processing = multi_processing

        self._init_shapefile(
            shapefile_path
        )

        self._check_missing(shapefile_path)

    def _init_shapefile(self, shapefile_path):
        self.shapefile = gpd.read_file(shapefile_path)
        # make sure the shapefile with wg84 projection
        self.shapefile = self.shapefile.to_crs(epsg=4326)

    # create directories for xEarthStat workflow

    def _check_missing(self, shapefile_path):
        os.makedirs(self.area_name, exist_ok=True)
        if not shapefile_path:
            print("Shapefile not provided")
            self.shapefile = input(
                "Please provide the path to the shapefile: ")

    def init_AgERA5_downloader(self, parameters, start_year, end_year, bounding_box):

        self.data_downloader = AgERA5Downloader(

            self.area_name,
            parameters,
            start_year,
            end_year,
            bounding_box
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

        self,
        max_workers=os.cpu_count(),
        all_touched=False,
        stat='mean'
    ):

        self._init_aggregation_workflow(

            self.workflow,
            all_touched=all_touched,
            stat=stat
        )

        print(f"Building {self.workflow} ({stat}) Datasets...")
        self.dataset_builder.build_datasets(max_workers=max_workers)
        print(f"{self.workflow} Datasets Aggregated Successfully")

    def _init_aggregation_workflow(

        self,
        workflow,
        max_workers=os.cpu_count(),
        all_touched=False,
        stat='mean'
    ):

        if workflow == 'dekadal':

            self.dataset_builder = DekadalDatasetBuilder(

                self.area_name,
                self.shapefile,
                multiprocessing=self.processing,
                max_workers=max_workers,
                all_touched=all_touched,
                stat=stat

            )

            self.workflow = workflow

        else:

            self.dataset_builder = DailyDatasetBuilder(

                self.area_name,
                self.shapefile,
                multiprocessing=self.processing,
                max_workers=max_workers,
                all_touched=all_touched,
                stat=stat

            )

            self.workflow = 'daily'

    def AgERA5_merged_csv(self, kelvin_to_celsius=False, output_name=None):
        get_merged_csv(self.area_name, self.workflow,
                       kelvin_to_celsius=kelvin_to_celsius, output_name=output_name)
        print("CSV Merged Successfully")

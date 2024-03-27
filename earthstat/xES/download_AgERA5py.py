import os
import concurrent.futures
from .cds_param import get_retrieve_params
from .cds_api_key_manager import APIKeyManager
try:
    import cdsapi
except ImportError:
    print("Please install the cdsapi package using 'pip install cdsapi'")


class AgERA5Downloader:
    def __init__(self, area_name, parameters, start_year, end_year, bounding_box):
        self.api_key_manager = APIKeyManager().add_cds_api_key()
        self.area_name = area_name
        self.parameters = parameters
        self.start_year = start_year
        self.end_year = end_year
        self.bounding_box = bounding_box

        self.cds = cdsapi.Client(progress=False)

    def download_AgERA5(self, num_requests):

        with concurrent.futures.ThreadPoolExecutor(
                max_workers=num_requests) as executor:
            tasks = [
                executor.submit(self._AgERA5_Requests, year, parameter)
                for year in range(self.start_year, self.end_year + 1)
                for parameter in self.parameters
            ]

            for future in concurrent.futures.as_completed(tasks):
                future.result()

    def _AgERA5_Requests(self, year, parameter):
        parameter_path = os.path.join(self.area_name, parameter)
        os.makedirs(parameter_path, exist_ok=True)
        retrieve_params = get_retrieve_params(
            parameter, self.bounding_box, year)
        self.cds.retrieve(
            'sis-agrometeorological-indicators',
            retrieve_params,
            f'{parameter_path}/{self.area_name}_{year}_{parameter}.zip'
        )

import cdsapi
from pathlib import Path


class APIKeyManager:
    def __init__(self):
        self.cds_api_key = None

    def add_cds_api_key(self):
        home_dir = Path.home()
        cdsapirc_path = home_dir / ".cdsapirc"

        if cdsapirc_path.exists():
            print(f"CDS API Key already exists in {cdsapirc_path}")
            with cdsapirc_path.open() as f:
                lines = f.readlines()
                for line in lines:
                    print(line)
            overwrite = input(
                "API Key found in {}. Do you want to overwrite it? (y/n): ".format(cdsapirc_path))
            if overwrite.lower() == "y":
                cdsApiKey = input("Please enter your CDS API Key: ")
                with cdsapirc_path.open("w") as f:
                    f.write("url: https://cds.climate.copernicus.eu/api/v2\n")
                    f.write(f"key: {cdsApiKey}\n")
                    self.cds = cdsapi.Client(progress=False)
                    return self.cds

            elif overwrite.lower() == "n":
                self.cds = cdsapi.Client(progress=False)
                return self.cds
            else:
                print("Invalid input. Please enter 'y' or 'n'")
                self.add_cds_api_key()
        else:
            self._request_and_save_key(cdsapirc_path)

    def _request_and_save_key(self, cdsapirc_path):
        cdsApiKey = input("Please enter your CDS API Key: ")
        with cdsapirc_path.open("w") as f:
            f.write("url: https://cds.climate.copernicus.eu/api/v2\n")
            f.write(f"key: {cdsApiKey}\n")
            print("CDS API Key added successfully")
        self.cds_api_key = cdsApiKey
        self.cds = cdsapi.Client(progress=False)
        return self.cds

    # # add CDS API key
    # def _add_cds_api_key(self):
    #     home_dir = Path.home()
    #     # Define the home directory and the path to the cdsapirc file
    #     cdsapirc_path = home_dir / ".cdsapirc"

    #     if cdsapirc_path.exists():
    #         print(f"CDS API Key already exists in {cdsapirc_path}\n")
    #         with cdsapirc_path.open() as f:
    #             lines = f.readlines()
    #             for line in lines:
    #                 print(line)
    #         overwrite = input(
    #             "API Key found in {}. Do you want to overwrite it? (y/n): ".format(cdsapirc_path))
    #         if overwrite.lower() == "y":
    #             cdsApiKey = input("Please enter your CDS API Key: ")
    #             with cdsapirc_path.open("w") as f:
    #                 f.write("url: https://cds.climate.copernicus.eu/api/v2\n")
    #                 f.write(f"key: {cdsApiKey}\n")
    #                 self.cds = cdsapi.Client(progress=False)

    #         elif overwrite.lower() == "n":
    #             self.cds = cdsapi.Client(progress=False)
    #         else:
    #             print("Invalid input. Please enter 'y' or 'n'")
    #     else:
    #         cdsApiKey = input("Please enter your CDS API Key: ")

    #         with cdsapirc_path.open("w") as f:
    #             f.write("url: https://cds.climate.copernicus.eu/api/v2\n")
    #             f.write(f"key: {cdsApiKey}\n")
    #             print("CDS API Key added successfully")

    #         self.cds = cdsapi.Client(progress=False)

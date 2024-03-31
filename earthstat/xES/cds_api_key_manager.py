try:
    import cdsapi
except ImportError:
    print("Please install the cdsapi package using 'pip install cdsapi'")
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
                f"API Key found in {cdsapirc_path}. Do you want to overwrite it? (y/n): ")
            if overwrite.lower() == "y":
                cdsApiKey = input("Please enter your CDS API Key: ")
                with cdsapirc_path.open("w") as f:
                    f.write("url: https://cds.climate.copernicus.eu/api/v2\n")
                    f.write(f"key: {cdsApiKey}\n")
                print("\nCDS API Key overwritten successfully")

            elif overwrite.lower() == "n":
                print("CDS API Key not overwritten")
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

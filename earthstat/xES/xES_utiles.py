import zipfile
import os
import glob
import re
import logging


def create_directories(area_name, build_dekadal_data=False):
    for param_folder in glob.glob(f'{area_name}/*'):
        try:
            os.makedirs(f'{param_folder}/Extracted', exist_ok=True)
            os.makedirs(f'{param_folder}/Aggregated_CSV', exist_ok=True)
            logging.info(f"Created directories in {param_folder}")
        except Exception as e:
            logging.error(
                f"Failed to create directories in {param_folder}: {e}")


def extract_zip(file_path, extract_path):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)


def extract_AgERA5_zips(area_name):
    logging.basicConfig(level=logging.INFO)
    downloaded_zip_files = [file for path in glob.glob(
        f'{area_name}/*') for file in glob.glob(f'{path}/*.zip')]
    year_pattern = re.compile(r'\d{4}')

    for file in downloaded_zip_files:
        filename = os.path.basename(file)
        year_match = year_pattern.search(filename)
        if year_match:
            year = year_match.group()
            parameter_path = os.path.dirname(file)
            try:
                extract_path = f'{parameter_path}/Extracted/{year}'
                extract_zip(file, extract_path)
                logging.info(f"Extracted {file} to {extract_path}")
            except Exception as e:
                logging.error(f"Failed to extract {file}: {e}")
        else:
            logging.warning(f"Year not found in filename: {filename}")


# Pre-compile the regular expression (do this outside the function)
year_pattern = re.compile(r'\d{4}')


def extract_file_details(path, year_regex=year_pattern):

    dir_file = os.path.dirname(path)
    parts = dir_file.split(os.sep)

    if len(parts) < 2:
        raise ValueError("Unexpected directory structure")

    csv_path = os.path.join(parts[0], parts[1])
    parameter = parts[1]
    file_name = os.path.basename(path)

    year_match = year_regex.search(file_name)
    year = year_match.group() if year_match else None

    return csv_path, parameter, year


def separate_path_components(path):
    normalized_path = path.replace('\\', '/')
    components = normalized_path.split('/')
    return components

import os
import re
from datetime import datetime
import glob


def savedFilePath(file_path):
    """
    Extracts and returns the directory and name of a file from its path.

    Args:
        file_path (str): The full path to the file.

    Returns:
        tuple: A tuple containing the file's directory and name.
    """
    file_dir = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)

    return file_dir, file_name


def extractDateFromFilename(filename):
    """
    Extracts a date string in 'YYYYMMDD' format from a filename.

    Args:
        filename (str): The name of the file containing a date.

    Returns:
        str: The extracted date string.
    """
    pattern = r'\d{8}'
    match = re.search(pattern, filename)
    date_str = match.group()
    return date_str


def convertDate(date):
    """
    Converts a date string from 'YYYYMMDD' format to a date object.

    Args:
        date (str): The date string in 'YYYYMMDD' format.

    Returns:
        datetime.date: The corresponding date object.
    """
    return datetime.strptime(date, '%Y%m%d').date()


def loadTiff(directory):
    """
    Loads and returns paths to all TIFF files in a specified directory.

    Args:
        directory (str): The directory to search for TIFF files.

    Returns:
        list: A list of paths to the TIFF files found in the directory.
    """
    paths = glob.glob(directory+'/*.tif')
    return paths

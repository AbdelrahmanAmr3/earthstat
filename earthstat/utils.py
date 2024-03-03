import os
import re
from datetime import datetime
import glob


def savedFilePath(file_path):

    file_dir = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)

    return file_dir, file_name


def extractDateFromFilename(filename):
    pattern = r'\d{8}'
    match = re.search(pattern, filename)
    date_str = match.group()
    return date_str


def convertDate(date):
    return datetime.strptime(date, '%Y%m%d').date()


def loadTiff(directory):
    paths = glob.glob(directory+'/*.tif')
    return paths

import glob
import os
import rasterio
from pyproj import CRS

from ..utils import extractDateFromFilename as exDate, convertDate as conDate


def loadData(directory_path, predictor):
    if not os.path.exists(directory_path):
        raise FileNotFoundError(
            f"The directory {directory_path} does not exist.")

    paths = glob.glob(os.path.join(directory_path, '*.tif'))
    if not paths:
        return "No TIFF files found. Please ensure the directory is correct and contains TIFF files."

    dates = [conDate(exDate(os.path.basename(path))) for path in paths]
    date_range = f"{min(dates)} to {max(dates)}" if dates else "No identifiable dates."

    with rasterio.open(paths[0]) as src:
        width, height = src.width, src.height
        crs = CRS(src.crs).name

    summary = (
        f"Data Summary:\n"
        f"- Found {len(paths)} TIFF files in '{directory_path}'.\n"
        f"- Data covers the period from {date_range}.\n"
        f"- Predictor: {predictor}\n"
        f"- Resolution: {width}x{height}\n"
        f"- Coordinate Reference System (CRS): {crs}\n"
    )

    print(summary)
    return paths

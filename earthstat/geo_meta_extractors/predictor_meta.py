import glob
import os
import rasterio
from pyproj import CRS

from ..utils import extractDateFromFilename as exDate, convertDate as convDate


def predictorMeta(predictor_dir, predictor_name):

    if not os.path.exists(predictor_dir):

        raise FileNotFoundError(
            f"The directory {predictor_dir} does not exist.")

    paths = glob.glob(os.path.join(predictor_dir, '*.tif'))
    if not paths:
        return "No TIFF files found. Please ensure the directory is correct and contains TIFF files."

    dates = [convDate(exDate(os.path.basename(path))) for path in paths]
    date_range = f"{min(dates)} to {max(dates)}" if dates else "No identifiable dates."

    with rasterio.open(paths[0]) as src:
        width, height = src.width, src.height
        crs = CRS(src.crs).name

    predictor_summary = {
        "predictor": predictor_name,
        "total_tiff_files": len(paths),
        "date_range": date_range,
        "directory": predictor_dir,
        "CRS": crs,
        "Extent": src.bounds,
        "Data Type": src.dtypes[0],
        "NoData Value": src.nodatavals[0],
        "Spatial Resolution": f"{width}x{height}",
        "Pixel Size": src.res
    }
    print("Predictor Summary:\n")
    print('\n'.join(f"{key}: {value}" for key,
          value in predictor_summary.items()))
    return predictor_summary

import rasterio
from pyproj import CRS
import geopandas as gpd
from rasterio.errors import CRSError
from .compatibility_utils import checkPixelSize, checkProjection


def checkDataCompatibility(raster_data_path, mask_path, shapefile_path):
    actions = {'resample_mask': False,
               'reproject_shapefile': False, 'is_compatible': True}

    try:
        with rasterio.open(mask_path) as mask, rasterio.open(raster_data_path) as raster_data:
            checkPixelSize(mask, raster_data)
            if mask.res != raster_data.res:
                actions['resample_mask'] = True
                actions['is_compatible'] = False

            mask_crs_name = CRS(mask.crs).name
            raster_data_crs_name = CRS(raster_data.crs).name
            checkProjection(mask_crs_name, raster_data_crs_name,
                            "mask", "predictor")
            if mask_crs_name != raster_data_crs_name:
                actions['is_compatible'] = False

        shapefile = gpd.read_file(shapefile_path)
        shapefile_crs_name = CRS(shapefile.crs).name
        checkProjection(raster_data_crs_name, shapefile_crs_name,
                        "raster data", "shapefile")
        if raster_data_crs_name != shapefile_crs_name:
            actions['reproject_shapefile'] = True
            actions['is_compatible'] = False

        return actions
    except CRSError as e:
        print(f"Error reading CRS data: {e}")
        return actions
    except Exception as e:
        print(f"An error occurred: {e}")
        return actions

import geopandas as gpd
from ..utils import savedFilePath
from pyproj import CRS


def shapefileMeta(shapefile_path):
    """
    Summarizes key metadata of a shapefile, including geometry types, CRS, extent,
    feature count, and attribute names. Assumes the shapefile can be read using
    GeoPandas.

    Args:
        shapefile_path (str): Path to the shapefile.

    Returns:
        dict: Contains 'Geometry Type', 'Coordinate Reference System (CRS)', 'Extent',
              'Feature Count', and 'Attributes' of the shapefile.
    """
    # Load the shapefile
    gdf = gpd.read_file(shapefile_path)
    crs = CRS(gdf.crs).name

    # Extracting essential information
    shapefile_meta = {
        "Geometry Type": gdf.geometry.type.unique(),
        "Coordinate Reference System (CRS)": crs,
        "Extent": gdf.total_bounds,
        "Feature Count": len(gdf),
        "Attributes": list(gdf.columns)
    }
    print("Shapefile Summary:\n")
    print('\n'.join(f"{key}: {value}" for key,
                    value in shapefile_meta.items()))

    return shapefile_meta

import geopandas as gpd
from ..utils import savedFilePath
from pyproj import CRS


def shapefileMeta(shapefile_path):
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

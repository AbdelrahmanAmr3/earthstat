import geopandas as gpd
import rasterio
from ..utils import savedFilePath


def reprojectShapefileToRaster(raster_data_path, shapefile_path):
    """
    Reprojects a shapefile to match the Coordinate Reference System (CRS) of a given raster file.

    Args:
        raster_data_path (str): Path to the raster file whose CRS is to be matched.
        shapefile_path (str): Path to the shapefile to be reprojected.

    Returns:
        str: Path to the reprojected shapefile saved in the same directory as the original.
    """
    file_dir, file_name = savedFilePath(shapefile_path)
    with rasterio.open(raster_data_path) as src:
        raster_crs = src.crs

    shapefile = gpd.read_file(shapefile_path)
    output_path = f'{file_dir}/reprojected_{file_name}'
    shapefile_reprojected = shapefile.to_crs(raster_crs)
    shapefile_reprojected.to_file(output_path)

    print(
        f"Shapefile reprojected to match raster CRS and saved to {output_path}")
    return output_path


def filterShapefile(shapefile_path, countries, country_column_name):
    """
    Filters a shapefile based on a list of country names within a specified column.

    Args:
        shapefile_path (str): Path to the shapefile to be filtered.
        countries (list of str): List of country names to filter by.
        country_column_name (str): Column name in the shapefile that contains country names.

    Returns:
        str: Path to the filtered shapefile saved in the same directory as the original.
    """
    file_dir, file_name = savedFilePath(shapefile_path)
    gdf = gpd.read_file(shapefile_path)
    filtered_gdf = gdf[gdf[country_column_name].isin(countries)]
    output_path = f'{file_dir}/filtered_{file_name}'
    filtered_gdf.to_file(output_path)
    print(f"Filtered shapefile saved to: {output_path}")
    return output_path

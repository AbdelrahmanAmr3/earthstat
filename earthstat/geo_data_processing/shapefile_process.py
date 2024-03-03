import geopandas as gpd
import rasterio
from ..utils import savedFilePath


def reprojectShapefileToRaster(raster_data_path, shapefile_path, output_shapefile_path):
    try:
        with rasterio.open(raster_data_path) as src:
            raster_crs = src.crs

        shapefile = gpd.read_file(shapefile_path)

        shapefile_reprojected = shapefile.to_crs(raster_crs)
        shapefile_reprojected.to_file(output_shapefile_path)

        print(
            f"Shapefile reprojected to match raster CRS and saved to {output_shapefile_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


def filterShapefile(shapefile_path, countries, country_column_name):

    file_dir, file_name = savedFilePath(shapefile_path)
    gdf = gpd.read_file(shapefile_path)
    filtered_gdf = gdf[gdf[country_column_name].isin(countries)]
    output_path = f'{file_dir}/filtered_{file_name}'
    filtered_gdf.to_file(output_path)
    print(f"Filtered shapefile saved to: {output_path}")
    return output_path
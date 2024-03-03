import rasterio
from pyproj import CRS


def maskSummary(raster_path):
    with rasterio.open(raster_path) as src:

        # Assuming there is a single band
        band_data = src.read(1, masked=True)

        # Compute minimum and maximum values
        min_value = band_data.min()
        max_value = band_data.max()
        crs = CRS(src.crs).name

        # Extracting essential information
        mask_summary = {
            "Mask_path": raster_path,
            "CRS": crs,
            "Extent": src.bounds,
            "Data Type": src.dtypes[0],
            "NoData Value": src.nodatavals[0],
            "Spatial Resolution": (src.width, src.height),
            "Pixel Size": src.res,
            "Min/Max Value": (min_value, max_value)
        }

        print("Mask Summary:\n")
        print('\n'.join(f"{key}: {value}" for key,
              value in mask_summary.items()))

        return mask_summary

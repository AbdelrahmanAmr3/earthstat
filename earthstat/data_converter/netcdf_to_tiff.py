import glob
import os
import rasterio
from rasterio.crs import CRS
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm


def netCDFToTiff(netcdf_file, output_dir, default_crs='EPSG:4326'):

    output_file = os.path.join(output_dir, os.path.basename(
        netcdf_file).replace(".nc", ".tif"))

    with rasterio.open(netcdf_file) as src:
        # Read the data
        data = src.read()
        transform = src.transform
        crs = src.crs
        if crs is None:
            crs = CRS.from_string(default_crs)
        kwargs = src.profile.copy()
        kwargs.update(
            driver='GTiff',
            height=src.height,
            width=src.width,
            count=data.shape[0],
            dtype=data.dtype,
            crs=crs,
            transform=transform,
            compress="lzw"  # compression
        )

        with rasterio.open(output_file, 'w', **kwargs) as dst:
            dst.write(data)


def convertToTIFF(input_dir):

    nc_files = glob.glob(os.path.join(input_dir, '*.nc'))
    output_dir = os.path.join(input_dir, 'predictor_tiff')
    os.makedirs(output_dir, exist_ok=True)

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(netCDFToTiff, file, output_dir)
                   for file in nc_files]
        for _ in tqdm(as_completed(futures), total=len(futures), desc="Converting Files"):
            pass

    return output_dir

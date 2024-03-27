import pandas as pd
import glob
import os
import xarray as xr
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm.auto import tqdm
from rasterio.features import geometry_mask
import rioxarray

try:
    import cupy as cp
    gpu_available = True

except ImportError:
    import numpy as cp
    gpu_available = False


class DailyDatasetBuilder:
    def __init__(self, area_name, shapefile, multiprocessing=False, max_workers=None, all_touched=False, stat='mean'):

        # Constructor
        self.area_name = area_name
        self.shapefile = shapefile
        self.all_touched = all_touched
        self.stat = stat

        if multiprocessing:
            self.multiprocessing = multiprocessing
            self.workers = max_workers if max_workers else os.cpu_count()
        else:
            self.multiprocessing = False

        self._processing_status()
        self.masks = self._compute_masks()

    def _processing_status(self):

        if gpu_available:
            print("GPU found. Aggregation will use GPU parallel computation.")
        else:
            print("No GPU or CUDA issue detected. Aggregation will use CPU.")

        if self.multiprocessing:
            print(f"Multiprocessing mode on, using {self.workers} cores.")
        else:
            print("Single processing mode on, suitable for Google Colab.")

    def _compute_masks(self):
        # Assuming the first dataset has the same spatial properties as the others
        sample_file = glob.glob(f'{self.area_name}/*/Extracted/*/*.nc')[0]
        ds = xr.open_dataset(sample_file)
        ds = ds.rio.write_crs("EPSG:4326")
        transform = ds.rio.transform()
        out_shape = (ds.rio.height, ds.rio.width)

        masks = []
        for _, geo_obj in self.shapefile.iterrows():
            mask = geometry_mask(
                [geo_obj['geometry']], out_shape=out_shape, transform=transform, invert=True, all_touched=self.all_touched)
            masks.append(mask)
        return masks

    def build_datasets(self, max_workers):
        os.makedirs(f'{self.area_name}_aggregated_daily_csv', exist_ok=True)
        var_folders = glob.glob(f'{self.area_name}/*/')

        if self.multiprocessing:
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(
                    self._daily_datasets, folder) for folder in var_folders]

                for future in tqdm(as_completed(futures), total=len(futures)):
                    future.result()

        else:
            for folder in tqdm(var_folders, desc='Processing folders'):
                self._daily_datasets(folder)

    def _daily_datasets(self, folder):
        aggregated_data = []
        file_list = glob.glob(f'{folder}/Extracted/*/*.nc')

        if self.multiprocessing:
            ds = xr.open_mfdataset(
                file_list, combine='by_coords', parallel=True)
        else:
            ds = xr.open_mfdataset(file_list, combine='by_coords')

        ds_variable = list(ds.data_vars)[0]

        ds = ds.rio.write_crs("EPSG:4326")
        gpu_data = cp.asarray(ds[ds_variable].values)

        for mask, (_, geo_obj) in tqdm(zip(self.masks, self.shapefile.iterrows()), total=len(self.masks), desc='Countries'):

            mask_gpu = cp.asarray(mask)
            masked_data_gpu = cp.where(mask_gpu, gpu_data, cp.nan)

            # axis=(1, 2) for 2D data (time, lat, lon)

            stats_functions = {
                'mean': cp.nanmean,
                'median': cp.nanmedian,
                'min': cp.nanmin,
                'max': cp.nanmax,
                'sum': cp.nansum
            }

            try:
                result_gpu = stats_functions[self.stat](
                    masked_data_gpu, axis=(1, 2))
            except KeyError:
                raise ValueError(
                    f"Invalid stat: {self.stat}. Options are 'mean', 'median', 'min', 'max', 'sum'.")

            if gpu_available:
                calculation_results = cp.asnumpy(result_gpu)
            else:
                calculation_results = result_gpu

            for date, mean_value in zip(ds.time.values, calculation_results):
                date_str = str(date)
                new_row = {
                    col: geo_obj[col] for col in self.shapefile.columns if col != 'geometry'}
                new_row.update(
                    {'date': date_str, f'{ds_variable}': mean_value})
                aggregated_data.append(new_row)

        if aggregated_data:
            df = pd.DataFrame(aggregated_data)
            df.to_csv(
                f'{self.area_name}_aggregated_daily_csv/AgERA5_{self.area_name}_{ds_variable}_dekadal.csv', index=False)
        else:
            print(f"No data found for {ds_variable}")

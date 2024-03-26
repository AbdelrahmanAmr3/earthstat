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

except ImportError:
    import numpy as cp


class DailyDatasetBuilder:
    def __init__(self, area_name, shapefile, multiprocessing=False, max_workers=None):
        self.area_name = area_name
        self.shapefile = shapefile
        self.masks = self._compute_masks()

        if multiprocessing:
            self.multiprocessing = multiprocessing
            self.workers = max_workers if max_workers else os.cpu_count()
        else:
            self.multiprocessing = False

        self._processing_status()

    def _processing_status(self):
        if self.multiprocessing:
            return f"Workflow will run as Multiprocessing with {self.workers} workers"
        else:
            return "Wrokflow will run as Single processing"

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
                [geo_obj['geometry']], out_shape=out_shape, transform=transform, invert=True, all_touched=False)
            masks.append(mask)
        return masks

    def build_datasets(self, max_workers):
        os.makedirs(f'{self.area_name}_Aggregated_Daily', exist_ok=True)
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
            mean_temp_gpu = cp.nanmean(masked_data_gpu, axis=(1, 2))
            mean_temp = cp.asnumpy(mean_temp_gpu)

            for date, mean_value in zip(ds.time.values, mean_temp):
                date_str = str(date)
                new_row = {
                    col: geo_obj[col] for col in self.shapefile.columns if col != 'geometry'}
                new_row.update(
                    {'date': date_str, f'{ds_variable}': mean_value})
                aggregated_data.append(new_row)

        if aggregated_data:
            df = pd.DataFrame(aggregated_data)
            df.to_csv(
                f'{self.area_name}_Aggregated_Daily/AgERA5_{self.area_name}_{ds_variable}_dekadal.csv', index=False)
        else:
            print(f"No data found for {ds_variable}")

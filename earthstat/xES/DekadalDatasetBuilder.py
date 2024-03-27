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


class DekadalDatasetBuilder():
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
        os.makedirs(f'{self.area_name}_Aggregated_dekadal_csv', exist_ok=True)
        var_folders = glob.glob(f'{self.area_name}/*/')

        if self.multiprocessing:
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(
                    self._dekadal_datasets, folder) for folder in var_folders]

                for future in tqdm(as_completed(futures), total=len(futures)):
                    future.result()

        else:
            for folder in tqdm(var_folders, desc='Processing folders'):
                self._dekadal_datasets(folder)

    @staticmethod
    def adjust_date(date):
        if 2 <= date.day <= 11:
            return date.replace(day=11)
        elif 12 <= date.day <= 21:
            return date.replace(day=21)
        elif 22 <= date.day <= 31:
            return date + pd.offsets.MonthBegin(1)
        else:
            return date

    def _dekadal_datasets(self, folder):

        aggregated_data = []
        file_list = glob.glob(f'{folder}/Extracted/*/*.nc')
        # Future enhancement we can add the option to run it parallel if the user use

        if self.multiprocessing:
            combined_ds = xr.open_mfdataset(
                file_list, combine='by_coords', parallel=True)
        else:
            combined_ds = xr.open_mfdataset(file_list, combine='by_coords')

        ds_variable = list(combined_ds.data_vars)[0]

        # Mask out the data for specific conditions
        first_year = combined_ds.time.dt.year.min().item()
        last_year = combined_ds.time.dt.year.max().item()

        mask_jan_1 = self._create_mask(combined_ds, first_year, 1, 1)
        mask_dec_22_31 = self._create_mask(
            combined_ds, last_year, 12, 22, True)
        combined_mask = mask_jan_1 & mask_dec_22_31

        ds_masked = combined_ds.where(combined_mask, drop=True)
        time_index = pd.to_datetime(ds_masked['time'].values)
        adjusted_dates = time_index.map(self.adjust_date)
        ds_masked['time'] = ('time', adjusted_dates)

        resampled_ds = self._resample_dataset(ds_masked, ds_variable)

        resampled_ds_variable = list(resampled_ds.data_vars)[0]
        gpu_data = cp.asarray(
            resampled_ds[resampled_ds_variable].values)

        for mask, (_, geo_obj) in tqdm(zip(self.masks, self.shapefile.iterrows()), total=len(self.masks), desc='Countries'):

            mask_gpu = cp.asarray(mask)
            masked_data_gpu = cp.where(
                mask_gpu, gpu_data, cp.nan)
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

            for date, result_value in zip(resampled_ds.time.values, calculation_results):
                date_str = str(date)
                new_row = {
                    col: geo_obj[col] for col in self.shapefile.columns if col != 'geometry'}
                new_row.update(
                    {'date': date_str, f'{ds_variable}': result_value})
                aggregated_data.append(new_row)

        if aggregated_data:
            df = pd.DataFrame(aggregated_data)
            df.to_csv(
                f'{self.area_name}_Aggregated_dekadal_csv/AgERA5_{self.area_name}_{ds_variable}_dekadal.csv', index=False)
        else:
            print(f"No data found for {ds_variable}")

    def _create_mask(self, ds, year, month, day, end_of_month=False):
        """Create a mask for the dataset based on specified conditions."""
        if end_of_month:
            return ~((ds.time.dt.year == year) & (ds.time.dt.month == month) & (ds.time.dt.day >= day))
        else:
            return ~((ds.time.dt.year == year) & (ds.time.dt.month == month) & (ds.time.dt.day == day))

    def _resample_dataset(self, ds, variable):
        """Resample dataset based on the variable type."""
        if variable in ['Precipitation_Flux', 'Solar_Radiation_Flux']:
            return ds.groupby('time').sum().astype('float32')
        elif variable in ['Temperature_Air_2m_Min_24h', 'Temperature_Air_2m_Max_24h']:
            return ds.groupby('time').min() if 'Min' in variable else ds.groupby('time').max()
        else:
            return ds.groupby('time').mean()

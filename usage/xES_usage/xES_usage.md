# xEarthStat for AgERA5 Usage

xEarthStat for AgERA5 allows users to download and aggregate AgERA5 climate data for a specified Region of Interest (ROI). This document outlines the installation process, setup, and usage instructions to get you started.

## Installation

To use xEarthStat for AgERA5, you first need to install the `earthstat` Python package. Run the following command in your Python environment:

```shell
pip install earthstat
```

## Getting Started

After installing the `earthstat` package, you can start using xEarthStat to download and aggregate data for your ROI. Here's a step-by-step guide:

### Step 1: Import xEarthStat

```python
from earthstat import xEarthStat as xES
```

### Step 2: Define Your Region of Interest (ROI)

Specify your ROI's name, bounding box, and the time range for the data you're interested in:

- **ROI Name** (`str`): Unique identifier for your ROI.
- **Bounding Box** (`list` of `float`): Define the north, west, south, and east coordinates of your ROI.
- **Time Range** (`int`): Specify the start and end years.

Example:

```python
ROI_name = 'EU_AgERA5'
start_year = 2000
end_year = 2001
ROI_bounding_box = [71, -31, 34.5, 40]  # Format: [north, west, south, east]
```

### Step 3: Set AgERA5 Parameters

List the climate parameters you want to download for your ROI:

```python
AgERA5_parameters = [
    'Maximum_Temperature', 'Minimum_Temperature', 'Mean_Temperature',
    'Solar_Radiation_Flux', 'Precipitation_Flux', 'Wind_Speed', 'Vapour_Pressure'
]
```
> <span style="color:red;">**Note & Caution:**</span> xEarthStat can just download 7 variables included in the table below.

| Variable                 | AgERA5 Parameter            | Statistical Download Type |
|--------------------------|-----------------------------|---------------------------|
| Maximum Temperature      | 2m_temperature              | 24_hour_maximum           |
| Minimum Temperature      | 2m_temperature              | 24_hour_minimum           |
| Mean Temperature         | 2m_temperature              | 24_hour_mean              |
| Solar Radiation Flux     | solar_radiation_flux        | -                         |
| Precipitation Flux       | precipitation_flux          | -                         |
| Wind Speed               | 10m_wind_speed              | 24_hour_mean              |
| Vapour Pressure          | vapour_pressure             | 24_hour_mean              |

### Step 4: Define the Shapefile Path

Provide the file path to your shapefile:

```python
shapefile_file_path = 'EU/admin_3.shp'
```

### Step 5: Initialize xEarthStat

Create an instance of xEarthStat with the specified parameters:
- `workflow`: The type of final generated dataset, `dekadal` for aggregated dekadal (1,11,21 of month) dataset, `daily` for daily dataset.   
- `multi_processing`: Enables parallel processing.

```python
EU_AgERA5 = xES(ROI_name,
                AgERA5_parameters,
                start_year,
                end_year,
                ROI_bounding_box,
                shapefile_path=shapefile_file_path,
                workflow='daily',
                multi_processing=True)
```

### Step 6: Download Data

Download the AgERA5 data for your ROI:
- `num_requests`: the number of downloading requests sends to CDS's API server until download all data.
- `extract`: Extract the downloaded AgERA5 zip files, set `False` if you don't want to extract them.

```python
EU_AgERA5.download_AgERA5(num_requests=6, 
                          extract=True)
```
> <span style="color:red;">**Note & Caution:**</span> Don't send more than 6 requests to the server. That may lead to pressure on the server and may result in blocking your API key from downloading.


### Step 7: Aggregate Data

xEarthStat's Aggregation process utilize the availability of GPU for parallel computation, and using the avilalble CPU cores for multiprocessing. it automatically detect if there is a GPU or not, if not it shift computational processing on CPU.

- `max_workers`: Default to total number of CPU's cores. You can change the number of cores that used in multiprocessing.
- `all_touched`: Default to `False` to just consider pixels within the geometry object. `True` to consider all touched pixels by geo-object. 
- `stat`: Default to `"mean"` to calculate the mean. There are other options, `"median"`, `"min"`, `"max"`, and `"sum"`.

```python
import os
cpu_cores = os.cpu_count()  # Get the number of all CPU cores
print(f'Number of CPU cores: {cpu_cores}')

EU_AgERA5.Aggregate_AgERA5(max_workers=cpu_cores, all_touched=False, stat='mean')
```

### Step 8: Export Aggregated Data

Optionally, merge all generated datasets' csv files into one merged csv for all aggregated variables:
- `kelvin_to_celsius`: To convert the temperature unit from kelvin to celsius.
- `output_name`: option to add the name of merged csv, it's default to `AgERA5_{ROI_name}_merged_parameters_{workflow}_{timestamp}.csv`

```python
EU_AgERA5.AgERA5_merged_csv(kelvin_to_celsius=False, 
                            output_name=None)
```
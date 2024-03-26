# EarthStat

[![image](https://img.shields.io/pypi/v/earthstat.svg)](https://pypi.python.org/pypi/earthstat)
[![Downloads](https://static.pepy.tech/badge/earthstat)](https://pepy.tech/project/earthstat)
[![image](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![image](https://img.shields.io/conda/vn/conda-forge/earthstat.svg)](https://anaconda.org/conda-forge/earthstat)
<a href="https://www.buymeacoffee.com/abdelrahmansaleh"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" height="20px"></a>

**A Python package for efficiently generating statistical datasets from raster data for spatial units.**


* GitHub repo: [https://github.com/AbdelrahmanAmr3/earthstat](https://github.com/AbdelrahmanAmr3/earthstat)
* Documentation: [https://abdelrahmanamr3.github.io/earthstat](https://abdelrahmanamr3.github.io/earthstat)
* PyPI: [https://pypi.org/project/earthstat](https://pypi.org/project/earthstat/)
* Free software: MIT license

EarthStat's Library Workflows's Notebooks:

* Main Workflow: [Google Colab](https://colab.research.google.com/github/AbdelrahmanAmr3/earthstat/blob/master/docs/examples/intro.ipynb),
[Binder](https://colab.research.google.com/github/AbdelrahmanAmr3/earthstat/blob/master/docs/examples/intro.ipynb)

* xEearthStat Workflow: [Google Colab](https://colab.research.google.com/github/AbdelrahmanAmr3/earthstat/blob/master/docs/examples/xES.ipynb),
[Binder]()


## Introduction

Drawing inspiration from participating in the AgML community's "Regional Crop Yield Forecasting" activity, I've developed a Python library to build benchmarks for training Machine Learning models. As the sole developer, I've focused on creating a tool that efficiently processes large volumes of TIFF files, extracting statistical information and converting raster data into easily manageable CSV files. This library is particularly suited for training Machine Learning (ML) models or conducting in-depth environmental analyses.

## EarthStat Workflow
This diagram illustrates the workflow of the geospatial data processing implemented in EarthStat from the initialized dataset to the created CSV file.

![Geospatial Data Processing Workflow](docs/assests/workflow.png)

## xEarthStat Workflow
This diagram illustrates the workflow of xEearthStat for AgERA5 data processing.

![Geospatial Data Processing Workflow](docs/assests/xES_workflow.png)

## EarthStat's Features

EarthStat revolutionizes the extraction of statistical information from geographic data, offering a seamless workflow for effective data management:

- **Data Initialization & Geo-metadata Readability:** Streamlines the incorporation of datasets into EarthStat workflow, and getting insights of vital geo-metadata for data (Raster, Mask, Shapefile).

- **netCDF Conversion:** Seamlessly integrates netCDF files into the workflow, converting them effortlessly into GeoTIFF format.

- **Data Compatibility Assurance:** Simplifies ensuring data compatibility, swiftly identifying and addressing geo data discrepancies among initialized data (Raster, Mask, Shapefile).

- **Automated Resolution of Compatibility Issues:** EarthStat resolves compatibility concerns, employing automatic resampling or reprojecting techniques for masks, and appropriate projection adjustments for shapefiles.

- **Targeted Region Selection:** Easily filter the shapefile to the targeted region.

- **Data Clipping:** Allows for clip raster data to specific shapefile boundaries.

- **Advanced Statistical Data Extraction:** Offers a variety of statistical aggregation methods.

- **Efficient Parallel Processing:** Leverages the power of multiprocessing, significantly accelerating data processing across extensive datasets for quicker, more efficient computation.

## EarthStat Python Library - Improvements Roadmap
### Data Processing and Scenario Management Enhancements 
- [x] offering more statistical options for aggregation.
- [ ] Introduce thresholding option for masks to refine data selection.
- [ ] Refactor Dataloader and Data Compatibility for no mask scenario.

### Automation for User Convenience
- [ ] Implement automatic detection of the lag between date ranges of predictor data.
- [ ] Automatically identify the column names for countries in the dataset.
- [ ] Enable users to specify date ranges for predictor data, improving data filtering capabilities.

### Add more Workflow utilizing different Geospatial libraries
- [ ] Workflow handle NetCDF files (Xarray + CuPy)

## Installation
To install EarthStat, ensure you have Python 3.8 or later installed. Then run:
```
pip install earthstat
```

## EarthStat Main Workflow Usage

### Initializing the Library
Import the library using:

```python
from earthstat import EarthStat
```

### Main Configuration Setup

Initialize the core settings:

`predictor_name`: The name of the predictor being used.  
`predictor_dir`: The directory where the predictor's related files are stored.  
`mask_file_path`: The file path to the mask file, used for calculate weighted mean or mask the raster.  
`shapefile_file_path`: Path to the shapefile containing geographical boundaries.
`selected_countries`: A list of countries - Region of interest (ROI).
`country_column_name`: The column's name in the dataset that contains country names.  
`invalid_values`: A list of values considered invalid within the dataset.

> **Important:** Be sure to set `invalid_values` to `None` if you do not wish to exclude unprocessed values from the dataset.

```python
predictor_name              = 'FPAR'
predictor_dir               = 'FPAR_Data'
mask_file_path              = 'crop_mask/Percent_Maize.tif'
shapefile_file_path         = 'shapefile/gaul1_asap.shp'
interested_ROI              = ["Norway", "Spain"] 
country_column_name         = 'adm0_name' 
invalid_values              =[255, 254, 251] # None-> No Invalid Values
```

> **Caution:** An increase in ROI size may lead to system crashes due to insuffienct RAM size, if you will not do parallel aggregation.


### Initialize the EarthStat object

```python
fpar_aggregator = EarthStat(predictor_name)
```
### Initialize Predictor/Data Directory, Mask, and Shapefile Path

Set up the foundational paths for your data processing pipeline. This includes initializing the directory for the predictor data, the path for the mask file, and the location of the shapefile. Each step is crucial for ensuring that the subsequent data processing and analysis can proceed smoothly.

Example Usage:

```python
# Initialize the predictor data directory
fpar_aggregator.initDataDir(predictor_dir)

# Set the path for the mask file
fpar_aggregator.initMaskPath(mask_file_path)

# Define the location of the shapefile
fpar_aggregator.initShapefilePath(shapefile_file_path)
```

### Checking Data Compatibility

Evaluate the compatibility of projections and pixel sizes across the mask, raster, and shapefile to ensure seamless data integration. This check confirms that the projection systems align for the mask, raster, and shapefile, and it also verifies that the pixel sizes between the raster and mask are compatible.

```python
fpar_aggregator.DataCompatibility()
```
### Resolving Data Compatibility Issues

This section addresses how to rectify issues identified by the data compatibility check. It focuses on resolving mismatches in pixel size between the raster and mask, or discrepancies in the Coordinate Reference System (CRS) among the raster, mask, and shapefile. The objective is to ensure uniformity in scale, resolution, and geospatial alignment across all datasets involved in the analysis.

- `rescale_factor`: This parameter allows for the adjustment of the data's scale. By default, it is set to `None`, maintaining the original scale of the data. To alter the scale, specify a new range with a tuple, such as `(0,100)`.
- `resampling_method`: This specifies the technique used to resample the data, with options including `"nearest"`, `"bilinear"`, `"cubic"`, and `"average"`. The default method is `"bilinear"`, suitable for a wide range of applications.

Example usage:

```python
# Disable rescaling and use default bilinear resampling
fpar_aggregator.fixCompatibilityIssues(rescale_factor=None, resampling_method="bilinear")

# Rescale data to a new range (0, 100) and use default bilinear resampling
fpar_aggregator.fixCompatibilityIssues(rescale_factor=(0,100), resampling_method="bilinear")
```

### Selecting Region of Interest (ROI)
Specify the area for data analysis by identifying the region of interest. Configure the target ROI and link it to the corresponding column that designates country or area names within the dataset.

```python
fpar_aggregator.selectRegionOfInterest(interested_ROI,
                                      country_column_name)
```
### Clipping Predictor Data
Clip the predictor data to the boundaries defined in a shapefile. If no specific Region of Interest (ROI) is selected by the previous function, the entire area within the main shapefile (Not filtered shapefile) will be used for clipping.

```python
fpar_aggregator.clipPredictor()
```
> **Note & Caution:** The Function is a multiprocessing process. Using the main shapefile without filtering may led to system crash or error due to the big amount of geometry objects in original shapefile.

### Executing Data Aggregation
Start data aggregation process, leveraging the clipped predictor data, resampled mask, and the filtered shapefile.

#### Parameters

- `use_mask` (**bool**): Specifies whether to apply a mask to the raster data. When set to `True`, the function will use the mask path provided (if applicable) to only process areas within the mask. Default is `False`.
  
- `invalid_values` (**list of int**): A list of pixel values to be treated as invalid and excluded from the aggregation. For example, `[255, 254, 251]` can be used to ignore certain values that represent no data or errors in the raster files.

- `calculation_mode` (**str**): Determines the mode of aggregation for pixel values. Supported modes include:
  - `"overall_mean"`: Calculates the mean of all valid pixel values across the raster dataset.
  - `"weighted_mean"`: Calculates the weighted mean of the valid pixel values using the mask values as weights. This mode is applicable only when `use_mask` is `True` and a valid `mask_file_path` is provided.
  - `"filtered_mean"`: Applies a filter using the validated mask values to mask the data before calculating the mean. This mode is intended for scenarios where only specific parts of the raster that meet certain conditions (defined by the mask) should contribute to the mean calculation.

- `all_touched` (**bool**): If set to `True`, all pixels touched by geometries will be included in the mask. If `False`, only pixels whose center is within the geometry or touching the geometry boundary will be included. Default is `False`.

Usage Example:

The following example demonstrates how to use `runAggregation` to process raster data without applying a mask, excluding specific invalid pixel values, calculating the overall mean of the valid pixels, and considering only pixels whose center is within the geometry:

```python
# Without Mask 
use_mask=False # True to use mask 
calculation_mode="overall_mean" # Options: weighted_mean, filtered_mean
all_touched=False

fpar_aggregator.runAggregation(use_mask, invalid_values, calculation_mode, all_touched)
```
In this example, it processes raster data by applying a mask, excluding defined invalid values and the values out of intersect between them, calculating the weighted mean using the mask values as weights values.

```python
# With Mask
use_mask=True
calculation_mode="weighted_mean"
all_touched=False

fpar_aggregator.runAggregation(use_mask, invalid_values, calculation_mode, all_touched)
```
The last option is applying a mask to exclude the defined invalid values with the values out of intersect between raster and mask, calculating the overall mean.

```python
# With Mask
use_mask=True
calculation_mode="filtered_mean"
all_touched=False

fpar_aggregator.runAggregation(use_mask, invalid_values, calculation_mode, all_touched)
```

### Parallel Processing with `runParallelAggregation`

The `runParallelAggregation` method is designed to process and aggregate raster data across multiple files in parallel, enhancing performance for large datasets. This method leverages multiple CPU cores to simultaneously process different portions of the data, reducing overall computation time.

Usage Example:

It follows the same structure of `runAggregation` and the same parameters.
```python
# Without Mask 
use_mask=False # True to use mask 
calculation_mode="overall_mean" # Options: weighted_mean, filtered_mean
all_touched=False

fpar_aggregator.runParallelAggregation(use_mask, invalid_values, calculation_mode, all_touched)
```

# Usage

## Installation
To install EarthStat, ensure you have Python 3.8 or later installed. Then run:
```
pip install earthstat
```

### Initializing the Library
Import the library using:
```python
from earthstat.earthstat import EarthStat
```

### Main Configuration Setup

Initialize the core settings: assign the predictor variable and data directory, specify the path to the crop mask, and define the shapefile path. Identify the column in the shapefile that contains area or country names.

> **Important:** Be sure to set `invalid_values` to `None` if you do not wish to exclude unprocessed values from the dataset.

```python
predictor_name              = 'FPAR'
predictor_dir               = 'FPAR_Data'
mask_file_path              = 'crop_mask/Percent_Maize.tif'
shapefile_file_path         = 'shapefile/gaul1_asap.shp'
interested_ROI              = ["Norway", "Spain"] 
country_column_name         = 'adm0_name' # Column's name contains countries in shapefile
invalid_values              =[255, 254, 251]  # Set None if no invalid Values
```
> :warning: **Caution:** An increase in ROI size may lead to system crashes due to insuffienct RAM size.


### Initialize the EarthStat object
```python
aggregate_fpar = EarthStat(predictor_name)
```
### Initialize Predictor/Data Directory, Mask, and Shapefile Path

Set up the foundational paths for your data processing pipeline. This includes initializing the directory for the predictor data, the path for the mask file, and the location of the shapefile. Each step is crucial for ensuring that the subsequent data processing and analysis can proceed smoothly.

#### Example Usage:

```python
# Initialize the predictor data directory
aggregate_fpar.initDataDir(predictor_dir)

# Set the path for the mask file
aggregate_fpar.initMaskPath(mask_file_path)

# Define the location of the shapefile
aggregate_fpar.initShapefilePath(shapefile_file_path)
```

### Checking Data Compatibility
Evaluate the compatibility of projections and pixel sizes across the mask, raster, and shapefile to ensure seamless data integration. This check confirms that the projection systems align for the mask, raster, and shapefile, and it also verifies that the pixel sizes between the raster and mask are compatible.
```python
aggregate_fpar.DataCompatibility()
```
### Resolving Data Compatibility Issues
This section addresses how to rectify issues identified by the data compatibility check. It focuses on resolving mismatches in pixel size between the raster and mask, or discrepancies in the Coordinate Reference System (CRS) among the raster, mask, and shapefile. The objective is to ensure uniformity in scale, resolution, and geospatial alignment across all datasets involved in the analysis.

- `rescale_factor`: This parameter allows for the adjustment of the data's scale. By default, it is set to `None`, maintaining the original scale of the data. To alter the scale, specify a new range with a tuple, such as `(0,100)`.
- `resampling_method`: This specifies the technique used to resample the data, with options including `"nearest"`, `"bilinear"`, `"cubic"`, and `"average"`. The default method is `"bilinear"`, suitable for a wide range of applications.

Example usage:

```python
# Disable rescaling and use default bilinear resampling
aggregate_fpar.fixCompatibilityIssues(rescale_factor=None, resampling_method="bilinear")

# Rescale data to a new range (0, 100) and use default bilinear resampling
aggregate_fpar.fixCompatibilityIssues(rescale_factor=(0,100), resampling_method="bilinear")
```

### Selecting Region of Interest (ROI)
Specify the area for data analysis by identifying the region of interest. Configure the target ROI and link it to the corresponding column that designates country or area names within the dataset.

```python
aggregate_fpar.selectRegionOfInterest(interested_ROI,
                                      country_column_name)
```
### Clipping Predictor Data
Clip the predictor data to the boundaries defined in the main shapefile. If no specific Region of Interest (ROI) is selected by the previous function, the entire area within the shapefile will be used for clipping.

```python
aggregate_fpar.clipPredictor()
```
> :warning: **Caution:** Using the main shapefile without filtering may led to system crash or error due to the big amount of objects in original shapefile.

### Executing Data Aggregation
Start data aggregation process, leveraging the clipped predictor data, resampled mask, and the selectively filtered shapefile to perform detailed analysis.

```python
aggregate_fpar.runAggregation()
```
> ❗ **Important:** Currently, the only available method for aggregation is weighted aggregation. Additional options for aggregation are under development and will be introduced soon.

### Parallel Processing with `runParallelAggregation`

The `runParallelAggregation` method is designed to process and aggregate raster data across multiple files in parallel, enhancing performance for large datasets. This method leverages multiple CPU cores to simultaneously process different portions of the data, reducing overall computation time.

#### Parameters

- `use_mask` (**bool**): Specifies whether to apply a mask to the raster data. When set to `True`, the function will use the mask path provided (if applicable) to only process areas within the mask. Default is `False`.
  
- `invalid_values` (**list of int**): A list of pixel values to be treated as invalid and excluded from the aggregation. For example, `[255, 254, 251]` can be used to ignore certain values that represent no data or errors in the raster files.

- `calculation_mode` (**str**): Determines the mode of aggregation for pixel values. Supported modes include:
  - `"overall_mean"`: Calculates the mean of all valid pixel values across the raster dataset.
  - `"weighted_mean"`: Calculates the weighted mean of the valid pixel values using the mask values as weights. This mode is applicable only when `use_mask` is `True` and a valid `mask_file_path` is provided.
  - `"filtered_mean"`: Applies a filter using the validated mask values to mask the data before calculating the mean. This mode is intended for scenarios where only specific parts of the raster that meet certain conditions (defined by the mask) should contribute to the mean calculation.

- `all_touched` (**bool**): If set to `True`, all pixels touched by geometries will be included in the mask. If `False`, only pixels whose center is within the geometry or touching the geometry boundary will be included. Default is `False`.

#### Usage Example

The following example demonstrates how to use `runParallelAggregation` to process raster data without applying a mask, excluding specific invalid pixel values, calculating the overall mean of the valid pixels, and considering only pixels whose center is within the geometry:

```python
use_mask=False # True to use mask 
calculation_mode="overall_mean" # Options: weighted_mean, filtered_mean
all_touched=False

aggregate_fpar.runParallelAggregation(use_mask, invalid_values, calculation_mode, all_touched)
```
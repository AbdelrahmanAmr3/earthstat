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
### EarthStat Main Workflow
#### Data Processing and Scenario Management Enhancements 
- [x] offering more statistical options for aggregation.
- [ ] Introduce thresholding option for masks to refine data selection.
- [ ] Refactor Dataloader and Data Compatibility for no mask scenario.

#### Automation for User Convenience
- [ ] Implement automatic detection of the lag between date ranges of predictor data.
- [ ] Automatically identify the column names for countries in the dataset.
- [ ] Enable users to specify date ranges for predictor data, improving data filtering capabilities.

### xEarthStat Workflow for AgERA5
- [ ] Option to mask the AgERA5's data with mask



## Installation
To install EarthStat, ensure you have Python 3.9 or later installed. 

Install with pip:
```
pip install earthstat
```
Install with Conda:
```
conda install conda-forge::earthstat
```
## EarthStat Usage
* [EarthStat Main Workflow](https://abdelrahmanamr3.github.io/earthstat/usage/main_usage)


* [xEearthStat for AgERA5 Workflow](https://abdelrahmanamr3.github.io/earthstat/usage/xES_usage)


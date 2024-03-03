# Welcome to EarthStat

[![image](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AbdelrahmanAmr3/earthstat/blob/master/docs/examples/intro.ipynb)
[![image](https://img.shields.io/pypi/v/earthstat.svg)](https://pypi.python.org/pypi/earthstat)
[![Downloads](https://static.pepy.tech/badge/earthstat)](https://pepy.tech/project/earthstat)
[![image](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![image](https://img.shields.io/conda/vn/conda-forge/earthstat.svg)](https://anaconda.org/conda-forge/earthstat)

**Inspired through participating in the AgML community's "Forecast Subnational Yield" activity, this Python library emerges as a vital tool for professionals and researchers engaged with remote sensing raster data. Designed with a focus on processing huge amount of TIFF files, our package excels at extracting statistical information for specific spatial units. By converting raster datasets into easily accessible CSV files. This library Ideal to prepare csv datasets for training Machine Learning (ML) models for different purposes. Also, significantly enhances the ability to leverage remote sensing data for impactful analyses (monitoring climate change, etc.). AgML community and the challenge of forecasting subnational agricultural yields has directly influenced the development of this library, ensuring it meets the high standards required for advanced environmental and agricultural data processing.**

## Features
EarthStat simplifies geospatial analysis by streamlining the extraction of statistical information from spatial units, providing a comprehensive toolset for efficient data processing and analysis:

- **Easy Data Preparation**: Define directories for raster files, shapefile paths, and masks effortlessly. Our library automates compatibility checks for pixel size, projection, and alignment between raster data (TIFF), mask, and shapefiles, ensuring smooth data integration.

- **Efficient ROI Selection & Raster Clipping**: Select your Region of Interest (ROI) with an intuitive filtering function. Clip raster data to your ROI quickly with just one line of code.

- **Advanced Data Aggregation**: aggregates raster data across selected spatial units but also intelligently masks the raster data during the aggregation process.

- **Comprehensive Data Export**: After aggregation, the library compiles the aggregated data along with related information from the shapefile into CSV files for each spatial unit.


## EarthStat Python Library - Improvements Roadmap
### Data Processing and Scenario Management Enhancements 
- [ ] offering more statistical options for aggregation.
- [ ] Introduce thresholding option for masks to refine data selection.
- [ ] Refactor Dataloader and Data Compatibility for no mask scenario.
- [ ] Merge individual data initialization functions into a single function, streamlining user interaction and input handling.

### Automation for User Convenience
- [ ] Implement automatic detection of the lag between date ranges of predictor data.
- [ ] Automatically identify the column names for countries in the dataset.
- [ ] Enable users to specify date ranges for predictor data, improving data filtering capabilities.

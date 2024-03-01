# earthstat


[![image](https://img.shields.io/pypi/v/earthstat.svg)](https://pypi.python.org/pypi/earthstat)
[![image](https://img.shields.io/conda/vn/conda-forge/earthstat.svg)](https://anaconda.org/conda-forge/earthstat)


**Inspired through participating in the AgML community's "Forecast Subnational Yield" activity, this Python library emerges as a vital tool for professionals and researchers engaged with remote sensing raster data. Designed with a focus on processing huge amount of TIFF files, our package excels at extracting statistical information for specific spatial units. By converting raster datasets into easily accessible CSV files. This library Ideal to prepare csv datasets for training Machine Learning (ML) models for different purposes. Also, significantly enhances the ability to leverage remote sensing data for impactful analyses (monitoring climate change, etc.). AgML community and the challenge of forecasting subnational agricultural yields has directly influenced the development of this library, ensuring it meets the high standards required for advanced environmental and agricultural data processing.**


-   Free software: MIT License
-   Documentation: https://AbdelrahmanAmr3.github.io/earthstat
    

## Features

## EarthStat Python Library - Improvements Roadmap
### Data Processing and Scenario Management Enhancements 
- [ ] Improve handle unwanted invalid values, allowing users to specify `None` as the preference.
- [ ] offering more statistical options for aggregation for each senario.
- [ ] mask initialization: indicate the scale range and important info for mask.
- [ ] Introduce thresholding options for masks to refine data selection.
- [ ] Allow users the option to skip rescaling the mask.
- [ ] Refactor Dataloader and Data Compatibility for no mask senario.
- [ ] Merge individual data initialization functions into a single function, streamlining user interaction and input handling.
- [ ] Refactor code to operate as a single class, enhancing code organization, modularity, and ease of use.

### Automation for User Convenience
- [ ] Implement automatic detection of the lag between date ranges of predictor data.
- [ ] Automatically identify the column names for countries in the dataset.
- [ ] Enable users to specify date ranges for predictor data, improving data filtering capabilities.

### Code Enhancement
- [ ] Better error handling and appropriate error responses.
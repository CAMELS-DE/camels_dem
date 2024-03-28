# Copernicus DEM GLO-30

## Description

*from: https://spacedata.copernicus.eu/de/collections/copernicus-digital-elevation-model*

The Copernicus DEM is a Digital Surface Model (DSM) that represents the surface of the Earth including buildings, infrastructure and vegetation. The Copernicus DEM is provided in 3 different instances: EEA-10, **GLO-30** and GLO-90. Data were acquired through the TanDEM-X mission between 2011 and 2015. The datasets were made available for use in 2019 and will be maintained until 2026.  
GLO-30 offers global coverage at a resolution of 30 metres. The dataset has a surface coverage of ~ 149 M km².


## Data retrieval for this repository

The necessary Copernicus DEM GLO-30 2023_1 data covering Germany is downloaded on the fly when running the Docker container from `prism-dem-open.copernicus.eu`. The DEM is downloaded in tiles which are merged to simplify extracting the catchment geometries. 

## Citation

https://doi.org/10.5270/ESA-c5d3d65
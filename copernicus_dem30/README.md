# Copernicus DEM GLO-30

## Description

Dockerized tool to extract and process data from the HUEK250 shapefile for CAMELS-DE.  
A .csv file is created in the `output_data` folder containing derived variables from the DEM for each catchment. The extracted variables are listed below.  
The results are copied to the camelsp `output_data` directory, where other tools process the data further and organize it in the folder structure.

## Container

### Build the container

```bash
docker build -t copernicus_dem30 .
```

### Run the container

To run the container, the local `input_data`, `output_data`, `scripts` and `camelsp/output_data` directories have to be mounted inside the container:

```bash
docker run -v ./input_data:/input_data -v ./output_data:/output_data -v ./scripts:/scripts -v /path/to/local/camelsp/output_data:/camelsp/output_data -it --rm copernicus_dem30
```

## Output variables

All variables are extracted from the DEM, only the variable `gauge_elevation` comes from the metadata of the gauge data providers and serves as a comparison to the heights extracted from the DEM.

- gauge_elevation [m a.s.l]
- gauge_elevation_from_dem [m a.s.l]
- mean_catchment_elevation_from_dem [m a.s.l]
- min_catchment_elevation_from_dem [m a.s.l]
- max_catchment_elevation_from_dem [m a.s.l]
- quantile0.05_catchment_elevation_from_dem [m a.s.l]
- quantile0.5_catchment_elevation_from_dem [m a.s.l]
- quantile0.95_catchment_elevation_from_dem [m a.s.l]
- stdev_catchment_elevation_from_dem [m a.s.l]

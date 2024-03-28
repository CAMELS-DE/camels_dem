# Copernicus DEM GLO-30

Dockerized tool to extract and process data from the Copernicus DEM GLO-30 tif file for CAMELS-DE.  
A folder is created in the `output_data` folder for the results of each catchment, in which a .csv file is saved for each of the superclasses with the variables listed below. In addition, plots of the superclasses in the catchment area are also generated. Extracted variables are copied to the camelsp `output_data` directory, where other tools process the data further and organize it in the folder structure.

## Container

### Build the container

```bash
docker build -t huek250 .
```

### Run the container

Follow the instructions in `input_data/README.md` to add the necessary input data to run the tool. 

To run the container, the local `input_data`, `output_data`, `scripts` and `camelsp/output_data` directories have to be mounted inside the container:

```bash
docker run -v ./input_data:/input_data -v ./output_data:/output_data -v ./scripts:/scripts -v /path/to/local/camelsp/output_data:/camelsp/output_data -it --rm huek250
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

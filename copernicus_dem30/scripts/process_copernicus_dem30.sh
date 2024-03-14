#!/bin/bash
# make directories to store the output data if they do not exist
mkdir -p /output_data/scripts

# logging
exec > >(tee -a /output_data/scripts/processing.log) 2>&1

# Start processing
echo "[$(date +%F\ %T)] Starting processing of Copernicus 30m DEM for the CAMELS-DE dataset..."

# Download the Copernicus 30m DEM
echo "[$(date +%T)] Downloading Copernicus 30m DEM..."
python /scripts/00_download_copernicus_dem30.py
cp /scripts/00_download_copernicus_dem30.py /output_data/scripts/00_download_copernicus_dem30.py
echo "[$(date +%T)] Downloaded and saved Copernicus 30m DEM with 00_download_copernicus_dem30.py"

# Generate a geopackage with MERIT Hydro catchments and a second geopackage with station locations
echo "[$(date +%T)] Generating geopackage with MERIT Hydro catchments and station locations..."
python /scripts/01_generate_stations_and_catchments_gpkg.py
cp /scripts/01_generate_stations_and_catchments_gpkg.py /output_data/scripts/01_generate_stations_and_catchments_gpkg.py
echo "[$(date +%T)] Generated geopackage with MERIT Hydro catchments and station locations with 01_generate_stations_and_catchments_gpkg.py"

# Calculate elevation statistics for all catchments and calculate the elevation of each station location
echo "[$(date +%T)] Calculating elevation statistics for all catchments and station locations..."
Rscript /scripts/02_extract_copernicus_dem30.R
cp /scripts/02_extract_copernicus_dem30.R /output_data/scripts/02_extract_copernicus_dem30.R
echo "[$(date +%T)] Saved elevation statistics for all catchments and station locations with 02_extract_copernicus_dem30.R"

# Change permissions of the output data
chmod -R 777 /camelsp/output_data/
chmod -R 777 /output_data/
chmod -R 777 /input_data/
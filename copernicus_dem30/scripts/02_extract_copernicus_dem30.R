# Calculate catchment and station elecation from DEM for all CAMELS-DE stations.
# @author: Alexander Dolich
#
# created: 2024/03/14
# modified: 2024/03/14

library(exactextractr)
library(terra)
library(sf)


# Load station locations
print("Loading station locations from /output_data/stations.gpkg ...")
stations <- sf::st_read("/output_data/stations.gpkg")

# Load catchment polygons
print("Loading catchment polygons from /output_data/catchments.gpkg ...")
catchments <- sf::st_read("/output_data/catchments.gpkg")

# Load merged Copernicus DEM raster
print("Loading merged Copernicus DEM raster from /input_data/dem/dem_merged.tiff ...")
dem <- terra::rast("/input_data/dem/dem_merged.tif")

# Transform catchments and stations to match the raster coordinate system
catchments <- st_transform(catchments, st_crs(dem))
stations <- st_transform(stations, st_crs(dem))

# Extract the dem height for all stations
print("Extracting the dem elevation for all stations ...")
extracted_stations <- extract(dem, stations, df = TRUE)

# Rename the column
names(extracted_stations)[names(extracted_stations) == "dem_merged"] <- "gauge_elevation_from_dem"

# Combine the extracted stations with the original stations
extracted_stations <- cbind(stations, extracted_stations)

# Drop column ID
extracted_stations <- subset(extracted_stations, select = -c(ID))

# Statistics to calculate for the catchments
stats <- c("mean", "min", "max", "quantile", "stdev")

# Extract the raster data (elevation) for all catchments
print("Extracting the raster data for all catchments ...")
extracted_catchments <- exact_extract(dem, catchments, fun = stats, quantiles = c(0.05, 0.5, 0.95),
                                      append_cols = "id", progress = FALSE,
                                      colname_fun = function(values, weights, fun_name, fun_value, nvalues, nweights) {
                                      if (is.na(fun_value)) {
                                          paste0(fun_name, '_catchment_elevation_from_dem')
                                      } else {
                                          paste0(fun_name, fun_value, '_catchment_elevation_from_dem')
                                      }
                                      })
# Rename id column
colnames(extracted_catchments)[1] <- "camels_id"

# Combine stations and catchments by camels_id
print("Combining the extracted stations with catchmetns ...")
dem_extracted <- merge(extracted_stations, extracted_catchments, by = "camels_id")

# Drop column geometry
dem_extracted <- st_set_geometry(dem_extracted, NULL)

# Save the extracted data
print("Saving the extracted data to /output_data/dem_extracted.csv ...")
write.csv(dem_extracted, "/output_data/dem_extracted.csv", row.names = FALSE)
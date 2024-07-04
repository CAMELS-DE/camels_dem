# Calculate catchment and station elecation from DEM for all CAMELS-DE stations.
# @author: Alexander Dolich
#
# created: 2024/03/14
# modified: 2024/03/14

library(exactextractr)
library(terra)
library(sf)

extract_dem_data <- function(catchments, stations, id_field_name_catchments, id_field_name_stations) {
  # Load station locations
  print(paste("Loading station locations from", stations, "..."))
  stations <- sf::st_read(stations)

  # Load catchment polygons
  print(paste("Loading catchment polygons from", catchments, "..."))
  catchments <- sf::st_read(catchments)

  # rename the id fields to "gauge_id"
  names(stations)[names(stations) == id_field_name_stations] <- "gauge_id"
  names(catchments)[names(catchments) == id_field_name_catchments] <- "gauge_id"

  # Load merged Copernicus DEM raster
  dem_path <- "/in/dem/dem_merged.tif"
  print(paste("Loading merged Copernicus DEM raster from", dem_path, "..."))
  dem <- terra::rast(dem_path)

  # Transform catchments and stations to match the raster coordinate system
  catchments <- sf::st_transform(catchments, sf::st_crs(dem))
  stations <- sf::st_transform(stations, sf::st_crs(dem))

  # Extract the dem height for all stations
  print("Extracting the dem elevation for all stations ...")
  extracted_stations <- terra::extract(dem, stations, df = TRUE)

  # Rename the column
  names(extracted_stations)[names(extracted_stations) == "dem_merged"] <- "gauge_elev"

  # Combine the extracted stations with the original stations
  extracted_stations <- cbind(stations, extracted_stations)

  # Drop column ID
  extracted_stations <- subset(extracted_stations, select = -c(ID))

  # Drop all columns except gauge_id and gauge_elevation_from_dem
  extracted_stations <- extracted_stations[, c("gauge_id", "gauge_elev")]

  # set gauge_lat, gauge_lon, gauge_easting, gauge_northing from geometry
  extracted_stations$gauge_lat <- sf::st_coordinates(extracted_stations)[, 2]
  extracted_stations$gauge_lon <- sf::st_coordinates(extracted_stations)[, 1]
  extracted_stations$gauge_northing <- sf::st_coordinates(sf::st_transform(extracted_stations, 3035))[, 2]
  extracted_stations$gauge_easting <- sf::st_coordinates(sf::st_transform(extracted_stations, 3035))[, 1]


  # Calculate area of catchments in km²
  catchments$area <- sf::st_area(catchments) / 1e6

  # Statistics to calculate for the catchments
  stats <- c("mean", "min", "max", "quantile")

  # Extract the raster data (elevation) for all catchments
  print("Extracting the raster data for all catchments ...")
  extracted_catchments <- exactextractr::exact_extract(dem, catchments, fun = stats, quantiles = c(0.05, 0.5, 0.95),
                                                       append_cols = c("gauge_id", "area"), progress = FALSE,
                                                       colname_fun = function(values, weights, fun_name, fun_value, nvalues, nweights) {
                                                       if (is.na(fun_value)) {
                                                         paste0('elev_', fun_name)
                                                       } else {
                                                         paste0('elev_', fun_value*100)
                                                       }
                                                       })

  # Combine stations and catchments by gauge_id
  print("Combining the extracted stations with catchments ...")
  dem_extracted <- merge(extracted_stations, extracted_catchments, by = "gauge_id")

  # Drop column geometry
  dem_extracted <- sf::st_set_geometry(dem_extracted, NULL)

  # put column elev_max at last column
  dem_extracted <- dem_extracted[, c(setdiff(names(dem_extracted), "elev_max"), "elev_max")]

  # round to 2 decimal places except for gauge_lat and gauge_lon
  dem_extracted[, -c(which(names(dem_extracted) %in% c("gauge_lat", "gauge_lon")))] <- round(dem_extracted[, -c(which(names(dem_extracted) %in% c("gauge_lat", "gauge_lon")))], 2)
  # round to 6 decimal places for gauge_lat and gauge_lon
  dem_extracted[, c(which(names(dem_extracted) %in% c("gauge_lat", "gauge_lon")))] <- round(dem_extracted[, c(which(names(dem_extracted) %in% c("gauge_lat", "gauge_lon")))], 6)

  # Save the extracted data
  print(paste("Saving the extracted data to /out/topographic_attributes.csv ..."))
  write.csv(dem_extracted, "/out/topographic_attributes.csv", row.names = FALSE)
}
# load json2aRgs for parameter parsing
library(json2aRgs)

# load the extract_corine function
source("extract_copernicus_dem30.R")

# get the parameters for the tool
params <- get_parameters()

# # get the data paths for the tool
data <- get_data(return_data_paths = TRUE)

# check if a toolname was set in env
toolname <- tolower(Sys.getenv("TOOL_RUN"))

# if no toolname was set, stop the script
if (toolname == "") {
  stop("No toolname was set in the environment. Please set the TOOL_RUN environment variable.")

} else if (toolname == "topographic_attributes_copernicus_dem30") {
  # run Python script to download the Copernicus DEM data if it does not exist yet
  system("python3 /src/download_copernicus_dem30.py")

  # extract the Copernicus DEM data
  extract_dem_data(catchments = data$catchments,
                   stations = data$stations,
                   id_field_name_catchments = params$id_field_name_catchments,
                   id_field_name_stations = params$id_field_name_stations)

} else {
  stop("The toolname '", toolname, "' is not supported.")
}

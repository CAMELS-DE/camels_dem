from camelsp import Station, get_metadata
import pandas as pd
import geopandas as gpd


def generate_stations_gpkg():
    """
    Generate a geopackage with the CAMELS-DE stations.

    """
    # Get the metadata for the CAMELS-DE dataset
    metadata = get_metadata()

    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame(metadata[["camels_id", "gauge_elevation"]], geometry=gpd.points_from_xy(metadata.lon, metadata.lat))

    # Save to geopackage
    gdf.to_file("/output_data/stations.gpkg", driver="GPKG")


def generate_merit_gpkg():
    """
    Generate a geopackage with MERIT Hydro catchments for all 
    stations in the CAMELS-DE dataset.

    """
    # Get the metadata for the CAMELS-DE dataset
    metadata = get_metadata()

    # Get a list of all camels_ids
    camels_ids = metadata["camels_id"].values

    # Create list to store the catchments
    all_catchments = []

    # Loop over all stations
    for camels_id in camels_ids:
        # Initialize station
        s = Station(camels_id)

        # Get MERIT Hydro catchment
        gdf = s.get_catchment("merit_hydro")

        # Append to list if MERIT Hydro catchment exists
        if gdf is not None:
            all_catchments.append(gdf)

    # Concatenate all catchments
    all_catchments = pd.concat(all_catchments)

    # Save to geopackage
    all_catchments.to_file("/output_data/catchments.gpkg", driver="GPKG")


if __name__ == "__main__":
    generate_stations_gpkg()
    generate_merit_gpkg()
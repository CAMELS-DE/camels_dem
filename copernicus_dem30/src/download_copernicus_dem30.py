import requests
import os
import math
import shutil
from glob import glob
import rasterio
from rasterio.merge import merge
import geopandas as gpd


def download_copernicus_dem30(catchments: gpd.GeoDataFrame):
    """
    Download the Copernicus 30m DEM tiles covering Germany and
    save to `/in/dem`.

    """
    # Bounding box of catchments + a buffer
    lon_min, lat_min, lon_max, lat_max = catchments.total_bounds
    
    # check if dem_merged.tif already exists
    if os.path.exists("/in/dem/dem_merged.tif"):
        # check if the bounding box of the catchments is within the bounding box of the dem_merged.tif
        with rasterio.open("/in/dem/dem_merged.tif") as dem:
            dem_bounds = dem.bounds
            if lon_min >= dem_bounds.left and lat_min >= dem_bounds.bottom and lon_max <= dem_bounds.right and lat_max <= dem_bounds.top:
                print("DEM already exists and covers the input catchments.")
                return
            else:
                # remove the existing dem_merged.tif
                os.remove("/in/dem/dem_merged.tif")
                print("Removed existing DEM as it does not cover the input catchments.")

    # floor and ceil the bounding box
    lon_min, lat_min, lon_max, lat_max = math.floor(lon_min), math.floor(lat_min), math.ceil(lon_max), math.ceil(lat_max)

    # GET all available DEM tiles
    response = requests.get("https://prism-dem-open.copernicus.eu/pd-desk-open-access/publicDemURLs/COP-DEM_GLO-30-DGED__2023_1", headers={"accept": "csv"})

    # Check if the request was successful
    if response.status_code == 200:
        # Make a list out of the response content
        urls = response.text.split("\n")

    # Filter the tiles that are within the bounding box
    tiles = []
    for url in urls:        
        # Extract the lat and lon from the URL
        if "DSM_10_N" in url:
            lat = int(url.split("DSM_10_N")[1].split("_00_")[0])
        if "_00_E" in url:
            lon = int(url.split("_00_E")[1].split("_00.tar")[0])
        if "_10_S" in url:
            lat = -int(url.split("DSM_10_S")[1].split("_00_")[0])
        if "_00_W" in url:
            lon = -int(url.split("_00_W")[1].split("_00.tar")[0])


        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            tiles.append(url)

    # Create folder to save dem data if it does not exist
    if not os.path.exists("/in/dem"):
        os.makedirs("/in/dem")

    # Download the tiles
    for tile in tiles:
        response = requests.get(tile)
        with open(f"/in/dem/{tile.split('/')[-1]}", "wb") as f:
            f.write(response.content)

    # Extract the .tif files from the tarballs and move them to the root of the dem folder
    for tarname in glob("/in/dem/*.tar"):
        fname = tarname.split("/")[-1].split(".tar")[0]

        # Extract the tarball
        os.system(f"tar -xf {tarname} -C /in/dem")

        # Move the .tif file to the root of the dem folder
        shutil.move(f"/in/dem/{fname}/DEM/{fname}_DEM.tif", "/in/dem")

        # Remove the tarball and the extracted folder
        os.remove(tarname)
        shutil.rmtree(f"/in/dem/{fname}/")

    print(f"Downloaded {len(tiles)} tiles of the Copernicus 30m DEM covering the input catchments.")


def merge_dem_tiles():
    """
    Merge the DEM tiles into a single raster file.

    """
    # Check if dem_merged.tif already exists
    if os.path.exists("/in/dem/dem_merged.tif"):
        return
    
    # List of all dem tiles
    dem_tiles = glob("/in/dem/*.tif")

    # Read the dem tiles
    src_files_to_mosaic = [rasterio.open(dem_tile) for dem_tile in dem_tiles]

    # Merge the dem tiles
    mosaic, out_trans = merge(src_files_to_mosaic)

    # Create CRS object
    out_crs = rasterio.crs.CRS.from_epsg(4326)

    # Save the merged dem
    with rasterio.open("/in/dem/dem_merged.tif", 'w', driver='GTiff', height=mosaic.shape[1], width=mosaic.shape[2], count=1, dtype=str(mosaic.dtype), crs=out_crs, transform=out_trans) as dest:
        dest.write(mosaic)

    # Remove the single dem tiles
    for dem_tile in dem_tiles:
        os.remove(dem_tile)

    print("Merged the DEM tiles into a single raster file `dem_merged.tif`.")


if __name__ == "__main__":
    from json2args.data import get_data_paths

    # get data paths
    data_paths = get_data_paths()

    # read catchments
    catchments = gpd.read_file(data_paths["catchments"])

    # transform catchments to EPSG:4326
    catchments = catchments.to_crs(epsg=4326)

    # download and merge dem tiles
    download_copernicus_dem30(catchments)
    merge_dem_tiles()

    # set permissions
    os.system("chmod -R 777 /in/dem")

import requests
import os
import shutil
from glob import glob
import rasterio
from rasterio.merge import merge


def download_copernicus_dem30():
    """
    Download the Copernicus 30m DEM tiles covering Germany and
    save to `/input_data/dem`.

    """
    # Bounding box of Germany + a buffer
    lat_min, lat_max, lon_min, lon_max = 46, 56, 5, 16

    # GET all available DEM tiles
    response = requests.get("https://prism-dem-open.copernicus.eu/pd-desk-open-access/publicDemURLs/COP-DEM_GLO-30-DGED__2023_1", headers={"accept": "csv"})

    # Check if the request was successful
    if response.status_code == 200:
        # Make a list out of the response content
        urls = response.text.split("\n")

    # Filter the tiles that are within the bounding box
    tiles = []
    for url in urls:
        # Skip those where url contains southing or westing
        if "_10_S" in url or "_00_W" in url:
            continue
        
        # Extract the lat and lon from the URL
        lat = int(url.split("DSM_10_N")[1].split("_00_")[0])
        lon = int(url.split("_00_E")[1].split("_00.tar")[0])

        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            tiles.append(url)

    # Create folder to save dem data if it does not exist
    if not os.path.exists("/input_data/dem"):
        os.makedirs("/input_data/dem")

    # Download the tiles
    for tile in tiles:
        response = requests.get(tile)
        with open(f"/input_data/dem/{tile.split('/')[-1]}", "wb") as f:
            f.write(response.content)

    # Extract the .tif files from the tarballs and move them to the root of the dem folder
    for tarname in glob("/input_data/dem/*.tar"):
        fname = tarname.split("/")[-1].split(".tar")[0]

        # Extract the tarball
        os.system(f"tar -xf {tarname} -C /input_data/dem")

        # Move the .tif file to the root of the dem folder
        shutil.move(f"/input_data/dem/{fname}/DEM/{fname}_DEM.tif", "/input_data/dem")

        # Remove the tarball and the extracted folder
        os.remove(tarname)
        shutil.rmtree(f"/input_data/dem/{fname}/")

    print(f"Downloaded {len(tiles)} tiles of the Copernicus 30m DEM covering Germany.")


def merge_dem_tiles():
    """
    Merge the DEM tiles into a single raster file.

    """
    # List of all dem tiles
    dem_tiles = glob("/input_data/dem/*.tif")

    # Read the dem tiles
    src_files_to_mosaic = [rasterio.open(dem_tile) for dem_tile in dem_tiles]

    # Merge the dem tiles
    mosaic, out_trans = merge(src_files_to_mosaic)

    # Create CRS object
    out_crs = rasterio.crs.CRS.from_epsg(4326)

    # Save the merged dem
    with rasterio.open("/input_data/dem/dem_merged.tif", 'w', driver='GTiff', height=mosaic.shape[1], width=mosaic.shape[2], count=1, dtype=str(mosaic.dtype), crs=out_crs, transform=out_trans) as dest:
        dest.write(mosaic)

    # Remove the single dem tiles
    for dem_tile in dem_tiles:
        os.remove(dem_tile)

    print("Merged the DEM tiles into a single raster file `dem_merged.tif`.")


if __name__ == "__main__":
    # Only run if the file /input_data/dem/dem_merged.tif does not exist
    if not os.path.exists("/input_data/dem/dem_merged.tif"):
        download_copernicus_dem30()
        merge_dem_tiles()
    else:
        print("The file /input_data/dem/dem_merged.tif already exists.")
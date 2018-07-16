import subprocess
import os

# creates a virtual raster mosaic
def create_vrt(tifs):

    vrtname = 'carbon_v4.vrt'
    os.system('gdalbuildvrt {0} {1}*.tif'.format(vrtname, tifs))

    return vrtname

# gets a list of all the unique biomass tiles
def list_tiles(tif_dir):

    # pipes the list of biomass tiles to a text document
    os.system('ls {}*.tif > carbon_tiles.txt'.format(tif_dir))

    file_list= []

    # Iterates through the text file to get the names of the tiles and appends them to list
    with open('carbon_tiles.txt', 'r') as tile:
        for line in tile:

            num = len(line)
            start = num - 13
            end = num - 5
            tile_short = line[start:end]

            file_list.append(tile_short)

    # Some tile names were in multiple ecoregions (e.g., 30N_110W in Palearctic and Nearctic). This gets only the unique tile names.
    file_list = set(file_list)

    print "There are", len(file_list), "tiles in the dataset"

    return file_list

# Gets the bounding coordinates for each tile
def coords(tile_id):
    NS = tile_id.split("_")[0][-1:]
    EW = tile_id.split("_")[1][-1:]

    if NS == 'S':
        ymax = -1 * int(tile_id.split("_")[0][:2])
    else:
        ymax = int(str(tile_id.split("_")[0][:2]))

    if EW == 'W':
        xmin = -1 * int(str(tile_id.split("_")[1][:3]))
    else:
        xmin = int(str(tile_id.split("_")[1][:3]))

    ymin = str(int(ymax) - 10)
    xmax = str(int(xmin) + 10)

    return str(ymax), str(xmin), str(ymin), str(xmax)

def process_tile(tile_id):

    print "Getting coordinates for ".format(tile_id), "..."
    ymax, xmin, ymin, xmax = coords(tile_id)
    print "Coordinates are: ymax-", ymax, "; ymin-", ymin, "; xmax-", xmax, "; xmin-", xmin

    print "Warping tile..."
    out = '{}_carbon.tif'.format(tile_id)
    warp = ['gdalwarp', '-t_srs', 'EPSG:4326', '-co', 'COMPRESS=LZW', '-tr', '0.00025', '0.00025', '-tap', '-te', xmin, ymin, xmax, ymax, '-dstnodata', '-9999', vrtname, out]
    subprocess.check_call(warp)
    print "Tile warped"

    print "Copying tile to s3..."
    s3_folder = 's3://WHRC-carbon/WHRC_V4/Processed/'
    cmd = ['aws', 's3', 'cp', out, s3_folder]
    subprocess.check_call(cmd)
    print "Tile copied to s3"


# Runs the process

tif_dir = '../raw/'

print "Creating vrt..."
vrtname = create_vrt(tif_dir)
print "vrt created"

print "Getting list of tiles..."
file_list = list_tiles(tif_dir)
print "Tile list retrieved"

print "Processing tile"
process_tile('10N_110E')
print "Tile processed"
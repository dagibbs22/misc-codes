import subprocess
import os
import multiprocessing

# Copies the tiles in the s3 folder to the spot machine.
def s3_to_spot(folder):
    dld = ['aws', 's3', 'cp', folder, '.', '--recursive', '--exclude', '*.xml']
    subprocess.check_call(dld)

# Creates a virtual raster mosaic
def create_vrt():

    vrtname = 'carbon_v4.vrt'
    os.system('gdalbuildvrt {0} *.tif'.format(vrtname))

    return vrtname

# Gets a list of all the unique biomass tiles
def list_tiles():

    # Makes a text file of the tifs in the folder
    os.system('ls *.tif > spot_carbon_tiles.txt')

    file_list= []

    # Iterates through the text file to get the names of the tiles and appends them to list
    with open('spot_carbon_tiles.txt', 'r') as tile:
        for line in tile:

            # Extracts the tile name from the file name
            num = len(line)
            start = num - 13
            end = num - 5
            tile_short = line[start:end]

            file_list.append(tile_short)

    # Some tile names were in multiple ecoregions (e.g., 30N_110W in Palearctic and Nearctic). This produces only the unique tile names.
    file_list = set(file_list)

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

# Chops the vrt into Hansen-compatible 10x10 chunks
def process_tile(tile_id):

    print "  Getting coordinates for {}".format(tile_id), "..."
    ymax, xmin, ymin, xmax = coords(tile_id)
    print "    Coordinates are: ymax-", ymax, "; ymin-", ymin, "; xmax-", xmax, "; xmin-", xmin

    print "  Warping tile..."
    out = '{}_carbon.tif'.format(tile_id)
    warp = ['gdalwarp', '-t_srs', 'EPSG:4326', '-co', 'COMPRESS=LZW', '-tr', '0.00025', '0.00025', '-tap', '-te', xmin, ymin, xmax, ymax, '-dstnodata', '-9999', vrtname, out]
    subprocess.check_call(warp)
    print "    Tile warped"

    print "  Copying tile to s3..."
    s3_folder = 's3://WHRC-carbon/WHRC_V4/Processed/'
    cmd = ['aws', 's3', 'cp', out, s3_folder]
    subprocess.check_call(cmd)
    print "    Tile copied to s3"


# Runs the process

tif_dir = '../raw/'

# Location of the tiles on s3
s3_locn = 's3://WHRC-carbon/WHRC_V4/As_provided/'

print "Checking if tiles are already downloaded..."

if os.path.exists('./Palearctic_MapV4_60N_010W.tif') == False:

    # Creates a list of all the tiles on s3
    print "  Copying raw tiles to spot machine..."
    s3_to_spot(s3_locn)
    print "    Raw tiles copied"

else:

    print "  Tiles already copied"

print "Creating vrt..."
vrtname = create_vrt()
print "  vrt created"

print "Getting list of tiles..."
file_list = list_tiles()
print "  Tile list retrieved. There are", len(file_list), "tiles in the dataset"

# for tile in file_list:
#     print "Processing tile {}".format(tile)
#     process_tile(tile)
#     print "   Tile processed"

count = multiprocessing.cpu_count()
pool = multiprocessing.Pool(count/2)
pool.map(process_tile, file_list)



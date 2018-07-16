import subprocess
import os
import multiprocessing

# Lists the tiles in a folder in s3
def s3_to_spot(source):

    ## For an s3 folder in a bucket using AWSCLI
    # Captures the list of the files in the folder
    out = subprocess.Popen(['aws', 's3', 'ls', source], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()

    # Writes the output string to a text file for easier interpretation
    s3_tiles = open("s3_tiles.txt", "w")
    s3_tiles.write(stdout)
    s3_tiles.close()

    file_list= []

    # Iterates through the text file to get the names of the tiles and appends them to list
    with open('s3_tiles.txt', 'r') as tile:
        for line in tile:

            num = len(line.strip('\n').split(" "))
            tile_name = line.strip('\n').split(" ")[num - 1]

            if "aux.xml" not in tile_name:

                tile_path = os.path.join(source, tile_name)

                file_list.append(tile_path)

    print file_list



    dld = ['aws', 's3', 'cp', source, '.']
    subprocess.check_call(dld)

# creates a virtual raster mosaic
def create_vrt(tifs):

    vrtname = 'carbon_v4.vrt'
    os.system('gdalbuildvrt {0} {1}*.tif'.format(vrtname, tifs))

    return vrtname

# gets a list of all the unique biomass tiles
def list_tiles(tif_dir, location):

    if location == "spot":

        # pipes the list of biomass tiles to a text document
        os.system('ls {}*.tif > spot_carbon_tiles.txt'.format(tif_dir))

    file_list= []

    # Iterates through the text file to get the names of the tiles and appends them to list
    with open('spot_carbon_tiles.txt', 'r') as tile:
        for line in tile:

            num = len(line)
            start = num - 13
            end = num - 5
            tile_short = line[start:end]

            file_list.append(tile_short)

    # Some tile names were in multiple ecoregions (e.g., 30N_110W in Palearctic and Nearctic). This gets only the unique tile names.
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

# if os.path.exists('../raw/') = False:
#
#     subprocess.check_call(['mkdir raw'])

tif_dir = '../raw/'

s3_to_spot('s3://WHRC-carbon/WHRC_V4/As_provided/')

# print "Creating vrt..."
# vrtname = create_vrt(tif_dir)
# print "  vrt created"
#
# print "Getting list of tiles..."
# file_list = list_tiles(tif_dir, "spot")
# print "  Tile list retrieved. There are", len(file_list), "tiles in the dataset"

# for tile in file_list:
#     print "Processing tile {}".format(tile)
#     process_tile(tile)
#     print "   Tile processed"

# count = multiprocessing.cpu_count()
# pool = multiprocessing.Pool(count/2)
# pool.map(process_tile, file_list)
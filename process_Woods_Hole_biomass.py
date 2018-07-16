import subprocess
import os

def create_vrt(tifs):
    vrtname = 'carbon_v4.vrt'
    os.system('gdalbuildvrt {0} {1}*.tif'.format(vrtname, tifs))

    return vrtname

def list_tiles(tif_dir):

    os.system('ls {}*.tif > carbon_tiles.txt'.format(tif_dir))

    file_list= []

    # Iterates through the text file to get the names of the tiles and appends them to list
    with open('carbon_tiles.txt', 'r') as tile:
        for line in tile:

            num = len(line)
            start = num - 14
            end = num - 5
            tile_short = line[start:end]
            print num
            print start
            print end
            print tile_short

            # num = len(line.strip('\n').split(" "))
            #
            # tile_name = line.strip('\n').split(" ")[num - 1]
            #
            # tile_short_name = tile_name.replace('_{0}.tif'.format("_carbon"), '')
            #
            # file_list.append(tile_short_name)

    # print file_list

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
    print "running: {}".format(tile_id)

    print "getting coordinates"
    ymax, xmin, ymin, xmax = coords(tile_id)
    print "coordinates are: ymax-", ymax, "; xmin-", xmin, "; ymin-", ymin, "; xmax-", xmax

    print "warping tile"
    out = '{}_carbon.tif'.format(tile_id)
    warp = ['gdalwarp', '-t_srs', 'EPSG:4326', '-co', 'COMPRESS=LZW', '-tr', '0.00025', '0.00025', '-tap', '-te', xmin, ymin, xmax, ymax, '-dstnodata', '-9999', vrtname, out]
    subprocess.check_call(warp)
    print "tile warped"

    print "copying tile to s3"
    s3_folder = 's3://WHRC-carbon/WHRC_V4/Processed/'
    cmd = ['aws', 's3', 'cp', out, s3_folder]
    subprocess.check_call(cmd)
    print "tile copied to s3"

tif_dir = '../raw/'

print "creating vrt"
vrtname = create_vrt(tif_dir)
print "vrt created"

print "getting list of tiles"
list = list_tiles(tif_dir)
print "tile list retrieved"

process_tile('10N_110E')
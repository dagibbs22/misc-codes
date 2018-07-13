import subprocess

def create_vrt():
    vrtname = 'carbon_v4.vrt'
    builtdvrt = ['gdalbuildvrt', vrtname, 'raw/*.tif']
    subprocess.check_call(builtdvrt)

    return vrtname

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

def iterate_tiles(tile_id):
    print "running: {}".format(tile_id)
    ymax, xmin, ymin, xmax = coords(tile_id)
    vrtname = create_vrt()
    out = '{}_carbon.tif'.format(tile_id)
    warp = ['gdalwarp', '-t_srs', 'EPSG:4326', '-tr', '.00025', '.00025', '-tap', '-te', xmin, ymin, xmax, ymax, '-dstnodata', '0', vrtname, out]

    subprocess.check_call(warp)

    s3_folder = 's3://WHRC-carbon/WHRC_V4/Processed/'
    cmd = ['aws', 's3', 'cp', out, s3_folder]
    subprocess.check_call(cmd)


iterate_tiles('10N_110E')
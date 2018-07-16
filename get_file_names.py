import boto3
import subprocess
import pandas

## For an s3 folder in a bucket using AWSCLI when accessed from a spot machine (used successfully in the carbon model utilities file)
# Lists the tiles in a folder in s3
def download_tiles(source):
    ## For an s3 folder in a bucket using AWSCLI
    # Captures the list of the files in the folder
    out = subprocess.Popen(['aws', 's3', 'ls', source], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()

    # Writes the output string to a text file for easier interpretation
    s3_tiles = open("s3_tiles.txt", "w")
    s3_tiles.write(stdout)
    s3_tiles.close()

    file_list = []

    # Iterates through the text file to get the names of the tiles and appends them to list
    with open('s3_tiles.txt', 'r') as tile:
        for line in tile:
            num = len(line.strip('\n').split(" "))
            tile_name = line.strip('\n').split(" ")[num - 1]

            file_list.append(tile_name)

    print file_list


# ## For an s3 folder in a bucket using AWSCLI
# # Gets the list of files and pipes them to a textfile
# pool= 'carbon'
# dest = 's3://gfw-files/sam/carbon_budget/carbon_030218/{}/'.format(pool)
# cmd = ['aws', 's3', 'ls', dest, '>', '{0}tiles.txt'.format(pool)]
# subprocess.check_call(cmd, shell=True)
#
# # Creates an empty list of files
# file_list = []
#
# # Iterates through the text file to get the names of the tiles and appends them to list
# with open('{0}tiles.txt'.format(pool), 'r') as tile:
#     for line in tile:
#         num = len(line.strip('\n').split(" "))
#
#         tile_name = line.strip('\n').split(" ")[num - 1]
#
#         tile_short_name = tile_name.replace('_{0}.tif'.format(pool), '')
#
#         file_list.append(tile_short_name)
#
# print file_list


# # For an s3 folder in a bucket using boto3
# # From https://stackoverflow.com/questions/35803027/retrieving-subfolders-names-in-s3-bucket-from-boto3
#
# # folders inside the bucket
# prefix = 'sam/carbon_budget/biomass_masked_30tcd'
#
# prefix_length = len(prefix)
#
# s3 = boto3.resource('s3')
#
# # identifies the buket
# bucket = s3.Bucket(name='gfw-files')
#
# # creates an empty list of files in the folder
# file_list = []
#
# # iterates through folders in bucket to get item names
# for obj in bucket.objects.filter(Prefix=prefix):
#
#     # corrects the file name
#     tile_name = '{}'.format(obj.key)
#     # tile_name = tile_name.replace('_totalc.tif', '')
#     tile_name = tile_name.replace(prefix, '')
#     tile_name = tile_name[1:9]
#
#     # adds the file to the end of the file list
#     file_list.append(tile_name)
#
# print(file_list)
#
# with open('listfile.txt', 'w') as filehandle:
#     for listitem in file_list:
#         filehandle.write('\'%s\', ' % listitem)


##For a local folder
# in_folder = r"C:\GIS\Carbon_model\total_carbon"
#
# file_list = os.listdir(in_folder)
#
# file_list_corrected = {x.replace('_totalc.tif', '') for x in file_list}
#
# with open('listfile.txt', 'w') as filehandle:
#     for listitem in file_list_corrected:
#         filehandle.write('\'%s\', ' % listitem)
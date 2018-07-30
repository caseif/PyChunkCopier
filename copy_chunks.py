#!/usr/bin/python3

import argparse
from math import floor
from os import makedirs, mkdir, path

REGION_RADIUS = 32
CHUNK_RADIUS = 16

SECTOR_SIZE = 4096

LOCAITON_DATA_LENGTH_BYTES = 1 * SECTOR_SIZE
HEADER_LENGTH = 2
HEADER_LENGTH_BYTES = HEADER_LENGTH * SECTOR_SIZE

SOURCE_BASE = "source"
TARGET_BASE = "target"
MERGED_BASE = "merged"

corner_1_x = 0
corner_1_z = 0
corner_2_x = 0
corner_2_z = 0

class Chunk:
    def __init__(self, timestamp, data):
        self.timestamp = timestamp
        self.data = data

parser = argparse.ArgumentParser(description='Utility for copying chunks chunks from one world to another.')
parser.add_argument('x1', type=int, help='X-coordinate of one of the corner chunks.')
parser.add_argument('z1', type=int, help='Z-coordinate of one of the corner chunks.')
parser.add_argument('x2', type=int, help='X-coordinate of the other corner chunk.')
parser.add_argument('z2', type=int, help='Z-coordinate of the other corner chunk.')

args = parser.parse_args()

min_corner = (min(args.x1, args.x2), min(args.z1, args.z2))
max_corner = (max(args.x1, args.x2), max(args.z1, args.z2))

source_dir = "%s/region" % SOURCE_BASE if path.exists("%s/region" % SOURCE_BASE) else SOURCE_BASE
target_dir = "%s/region" % TARGET_BASE if path.exists("%s/region" % TARGET_BASE) else TARGET_BASE
merged_dir = "%s/region" % MERGED_BASE

def process_region_file(region_x, region_z):
    print("Processing region (%d, %d)..." % (region_x, region_z))

    region_file = "r.%d.%d.mca" % (region_x, region_z)

    old_region_file = "%s/%s" % (source_dir, region_file)
    new_region_file = "%s/%s" % (target_dir, region_file)

    if not path.isfile(old_region_file):
        print("Old region file %s does not exist, skipping." % region_file)
        return
    
    if not path.isfile(new_region_file):
        print("New region file %s does not exist, skipping." % region_file)
        return

    region_chunk_min_x = region_x * REGION_RADIUS
    region_chunk_min_z = region_z * REGION_RADIUS

    with open(old_region_file, mode='rb') as file:
        old_file_content = file.read()

    old_location_data = old_file_content[0:LOCAITON_DATA_LENGTH_BYTES]
    old_timestamp_data = old_file_content[LOCAITON_DATA_LENGTH_BYTES:HEADER_LENGTH_BYTES]
    old_chunk_data = old_file_content[HEADER_LENGTH_BYTES:]

    with open(new_region_file, mode='rb') as file:
        new_file_content = file.read()

    new_location_data = new_file_content[0:LOCAITON_DATA_LENGTH_BYTES]
    new_timestamp_data = new_file_content[LOCAITON_DATA_LENGTH_BYTES:HEADER_LENGTH_BYTES]
    new_chunk_data = new_file_content[HEADER_LENGTH_BYTES:]

    chunks = {}

    count_old = 0
    count_new = 0

    size = 8192

    for chunk_z in range(0, REGION_RADIUS):
        for chunk_x in range(0, REGION_RADIUS):
            chunk_x_abs = chunk_x + region_chunk_min_x
            chunk_z_abs = chunk_z + region_chunk_min_z

            header_addr = 4 * ((chunk_x) + (chunk_z) * REGION_RADIUS)

            use_old = chunk_x_abs >= min_corner[0] and chunk_x_abs <= max_corner[0] and chunk_z_abs >= min_corner[1] and chunk_z_abs <= max_corner[1]

            location_data = old_location_data if use_old else new_location_data

            location = int.from_bytes(location_data[slice(header_addr, header_addr + 3)], byteorder='big', signed=False) - HEADER_LENGTH

            length = location_data[header_addr + 3]

            if length == 0:
                print("Chunk (%d, %d) not present." % (chunk_x, chunk_z))
                continue

            if use_old:
                count_old += 1
            else:
                count_new += 1

            size += length * 4096

            timestamp_data = old_timestamp_data if use_old else new_timestamp_data

            timestamp = int.from_bytes(timestamp_data[slice(header_addr, header_addr + 4)], byteorder='big', signed=False)

            chunk_data_blob = old_chunk_data if use_old else new_chunk_data

            data = chunk_data_blob[slice(location * SECTOR_SIZE, (location + length) * SECTOR_SIZE)]

            chunks[(chunk_x, chunk_z)] = Chunk(timestamp, data)

    print("Loaded %d old chunks and %d new chunks from %s." % (count_old, count_new, region_file))

    merged_location_header = bytearray()
    merged_timestamp_header = bytearray()
    merged_chunk_data = bytearray()

    offset = HEADER_LENGTH

    data_len = 0

    for chunk_z in range(0, REGION_RADIUS):
        for chunk_x in range(0, REGION_RADIUS):
            key = (chunk_x, chunk_z)
            
            if key in chunks:
                data_len += len(chunks[key].data)

                merged_chunk_data += chunks[key].data
                
                length = len(chunks[key].data) // SECTOR_SIZE

                merged_location_header += offset.to_bytes(3, byteorder='big')
                merged_location_header += length.to_bytes(1, byteorder='big')

                merged_timestamp_header += chunks[key].timestamp.to_bytes(4, byteorder='big')

                offset += length

    merged_data = merged_location_header + merged_timestamp_header + merged_chunk_data

    if not path.exists(merged_dir):
        makedirs(merged_dir)

    with open("%s/%s" % (merged_dir, region_file), 'wb') as merged_file:
        merged_file.write(bytes(merged_data))

    print("Wrote merged data to %s." % merged_file.name)

min_region = (floor(min_corner[0] / 32), floor(min_corner[1] / 32))
max_region = (floor(max_corner[0] / 32), floor(max_corner[1] / 32))

for region_x in range(min_region[0], max_region[0] + 1):
    for region_z in range(min_region[1], max_region[1] + 1):
        process_region_file(region_x, region_z)

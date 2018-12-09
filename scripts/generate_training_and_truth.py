from argparse import ArgumentParser
from pathlib import Path
from shutil import copyfile
from tqdm import tqdm
from util import bingmaps

import csv
import cv2
import json
import numpy as np
import requests
import urllib


def load_buildings_from_file(buildingCsv):
    firstLine = True

    with open(buildingCsv, 'r') as csv:
        for row in csv.readlines():
            
            if firstLine == True:
                firstLine = False
            else:
                tokens = row.strip().split(",")
                yield {
                    "project_id" : tokens[0],
                    "task_id" : tokens[1],
                    "way_id" : tokens[2],
                    "bounding_box" : tokens[3:]
                }
    

def bounding_box_to_lat_lon_list(bounding_box):
    box = []
    for i in range(0, len(bounding_box), 2):
        (lat, lon) = float(bounding_box[i]), float(bounding_box[i+1])
        box.append([lat, lon])
    return box


def bounding_box_to_pixel_coords(bounding_box_lat_lon, zoom_level):
    box = []
    for (lat, lon) in bounding_box_lat_lon:
        (x, y) = bingmaps.pixel_xy_relative_to_tile(lat, lon, zoom_level)
        box.append([x, y])
    return box


def bounding_box_entirely_in_same_tile(bounding_box_lat_lon, zoom_level):
    previous_quadkey = None

    for (lat, lon) in bounding_box_lat_lon:
        quadkey = bingmaps.quadkey_containing_lat_lon(lat, lon, zoom_level)

        if previous_quadkey == quadkey or previous_quadkey is None:
            previous_quadkey = quadkey
        else:
            return False

    return True


def get_output_folder(project_id, task_id, zoom_level, output_folder):
    path = Path(output_folder) / Path(str(project_id)) / Path(str(task_id)) / Path(str(zoom_level))
    path.mkdir(parents=True, exist_ok=True) 
    return path


def get_output_paths(project_id, task_id, zoom_level, output_folder, quadkey):
    output_folder = get_output_folder(project_id, task_id, zoom_level, output_folder)
    truth_name = "a%s_truth.jpeg" % quadkey
    tile_name = "a%s.jpeg" % quadkey

    return (output_folder / tile_name, output_folder / truth_name)


def get_maptile_path(project_id, task_id, zoom_level, maptile_folder, quadkey):
    file_name = "a%s.jpeg" % quadkey
    path = Path(maptile_folder) / Path(str(project_id)) / Path(str(task_id)) / Path(str(zoom_level)) / file_name
    return path


def parse_arguments():    
    parser = ArgumentParser() 
    parser.add_argument("-b", "--buildingCsv", dest="buildingCsv",
                        help="A csv of verified buildings, their polygons, and their task info")
    parser.add_argument("-z", "--zoomLevel", dest="zoomLevel",
                        help="Level of zoom at which to prepare training data")
    parser.add_argument("-m", "--mapTiles", dest="mapTiles",
                        help="Lookup map tiles in this folder structure", default="data/map_tiles")
    parser.add_argument("-o", "--outputFolder", dest="outputFolder",
                        help="Save processed map tiles into this folder", default="data/training")

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_arguments()

    output_folder = None
    url = None
    zoom_level = int(args.zoomLevel)

    quadkey_buildings = {}
    quadkey_meta = {}

    for task in load_buildings_from_file(args.buildingCsv):
        project_id = task["project_id"]
        task_id = task["task_id"]
        way_id = task["way_id"]
        bounding_box = bounding_box_to_lat_lon_list(task["bounding_box"])

        if bounding_box_entirely_in_same_tile(bounding_box, zoom_level):
            quadkey = bingmaps.quadkey_containing_lat_lon(bounding_box[0][0], bounding_box[0][1], zoom_level)
            bounding_box_pixel_coords = bounding_box_to_pixel_coords(bounding_box, zoom_level)

            if quadkey in quadkey_buildings:
                quadkey_buildings[quadkey].append(bounding_box_pixel_coords)
            else:
                quadkey_buildings[quadkey] = [bounding_box_pixel_coords]

            quadkey_meta[quadkey] = {
                "project_id" : project_id,
                "task_id" : task_id
            }
        
    print("Found %s map tiles containing complete quadkeys. Writing output under %s" % (len(quadkey_buildings.keys()), args.outputFolder))        
            
    for (quadkey, bounding_boxes) in tqdm(quadkey_buildings.items()):
        project_id = quadkey_meta[quadkey]["project_id"]
        task_id = quadkey_meta[quadkey]["task_id"]

        maptile_path = get_maptile_path(project_id, task_id, zoom_level, args.mapTiles, quadkey)
        if maptile_path.exists():
            (output_tile, output_truth) = get_output_paths(project_id, task_id, zoom_level, args.outputFolder, quadkey)
            
            truth = np.zeros([256, 256, 3], np.uint8)
            
            for bounding_box in bounding_boxes:
                cv2.fillPoly(truth, np.array([bounding_box], dtype='int32'), (255, 255, 255))
            
            cv2.imwrite(str(output_truth), truth)

            copyfile(str(maptile_path), str(output_tile))



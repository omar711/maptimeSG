from argparse import ArgumentParser
from util import bingmaps
from pathlib import Path
from util import bingmaps

import csv
import json
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

    for task in load_buildings_from_file(args.buildingCsv):
        project_id = task["project_id"]
        task_id = task["task_id"]
        way_id = task["way_id"]
        bounding_box = bounding_box_to_lat_lon_list(task["bounding_box"])

        if bounding_box_entirely_in_same_tile(bounding_box, zoom_level):
            print("IN")
        else:
            print("OUT")
        #output_folder = get_output_folder(project_id, task_id, zoom_level, args.outputFolder)



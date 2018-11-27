from argparse import ArgumentParser
from pathlib import Path

import csv
import json
import requests



def fetch_map_metadata(center_lat, center_lon, api_key):
    params = {
        "zl" : 15,
        "o" : "json",
        "key" : api_key
    }

    center = str(center_lat) + "," + str(center_lon)
    r = requests.get("https://dev.virtualearth.net/REST/V1/Imagery/Metadata/Aerial/" + center, params)

    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        r.raise_for_status()


def get_output_file(project_id, task_id, output_folder):
    filename = "%s-%s-buildings.csv" % (project_id, task_id)
    path = Path(output_folder)
    path.mkdir(parents=True, exist_ok=True) 
    return path / filename 


def load_api_key(location=".bing_api_key"):
    with open(location) as key_file:
        return key_file.read().strip()


def parse_arguments():    
    parser = ArgumentParser() 
    parser.add_argument("-v", "--validatedBuildings", dest="validatedBuildings",
                        help="A csv of validated building bounding boxes")
    parser.add_argument("-o", "--outputFolder", dest="outputFolder",
                        help="Save map tiles into this folder", default="data/map_tiles")

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_arguments()
    api_key = load_api_key()

    m = fetch_map_metadata(16.851862450285, 95.8293701000399, api_key)
    print(m["resourceSets"][0])


# TODO: read this https://msdn.microsoft.com/en-us/library/bb259689.aspx 
# Figure out a neat and minimal web request way to take our large task bounding box, 
# then enumerate all map tile urls for any given zoom level.  
# We'll need to track tiles + coordinates so we can later pair them with building polygons

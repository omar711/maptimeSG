from argparse import ArgumentParser
from pathlib import Path
from util import bingmaps

import csv
import json
import requests
import urllib



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


def fetch_and_save_image(url, output_folder):
    r = requests.get(url, stream=True)
    
    if r.status_code == requests.codes.ok:
        parsed = urllib.parse.urlparse(url)
        filename = parsed.path.rpartition('/')[2]

        with open(output_folder / filename, 'wb') as f:
            for chunk in r:
                f.write(chunk)
    else:
        r.raise_for_status()


def get_image_url(map_metadata):
    return map_metadata["resourceSets"][0]["resources"][0]["imageUrl"]


def image_url_for_quadkey(image_url, quadkey):
    url = image_url._replace(path="/tiles/a%s.jpeg" % quadkey)
    return urllib.parse.urlunparse(url)


def get_output_file(project_id, task_id, output_folder):
    filename = "%s-%s-buildings.csv" % (project_id, task_id)
    path = Path(output_folder)
    path.mkdir(parents=True, exist_ok=True) 
    return path / filename 


def load_api_key(location=".bing_api_key"):
    with open(location) as key_file:
        return key_file.read().strip()


def load_tasks_from_file(taskCsv):
    with open(taskCsv, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row
    

def get_output_folder(project_id, task_id, zoom_level, output_folder):
    path = Path(output_folder) / Path(str(project_id)) / Path(str(task_id)) / Path(str(zoom_level))
    path.mkdir(parents=True, exist_ok=True) 
    return path


def parse_arguments():    
    parser = ArgumentParser() 
    parser.add_argument("-t", "--taskCsv", dest="taskCsv",
                        help="A csv of tasks and their bounding boxes")
    parser.add_argument("-z", "--zoomLevel", dest="zoomLevel",
                        help="Level of zoom at which to retrieve tiles")
    parser.add_argument("-o", "--outputFolder", dest="outputFolder",
                        help="Save map tiles into this folder", default="data/map_tiles")

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_arguments()

    output_folder = None
    url = None
    zoom_level = int(args.zoomLevel)
    api_key = load_api_key()

    for task in load_tasks_from_file(args.taskCsv):
        project_id = task["project_id"]
        task_id = task["task_id"]
        min_lat = float(task["min_lat"])
        min_lon = float(task["min_lon"])
        max_lat = float(task["max_lat"])
        max_lon = float(task["max_lon"])

        if output_folder is None:
            output_folder = get_output_folder(project_id, task_id, zoom_level, args.outputFolder)
            print("Created output folder at %s" % (output_folder, ))

        if url is None:
            map_metadata = fetch_map_metadata(min_lat, min_lon, api_key)
            image_url = get_image_url(map_metadata)
            url = urllib.parse.urlparse(image_url)

        quadkeys = bingmaps.enumerate_quadkeys_in_box(min_lat, min_lon, max_lat, max_lon, zoom_level)
        for quadkey in quadkeys:
            image_url = image_url_for_quadkey(url, quadkey)
            fetch_and_save_image(image_url, output_folder)

        print("Written %s tiles to %s" % (len(quadkeys), output_folder))


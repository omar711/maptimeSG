from argparse import ArgumentParser
from pathlib import Path

import csv
import json
import requests


def get_bounding_box(element, node_coords):
    bbox = []
    nodes = element["nodes"]

    for node in nodes:
        coords = node_coords[node]
        bbox.append(coords["lat"])
        bbox.append(coords["lon"])

    return bbox

def convert_to_polygons(raw_buildings):
    nodes = {}

    # Enumerate nodes
    for element in raw_buildings["elements"]:
        element_type = element["type"]
        element_id = element["id"]

        if element_type == "node":
            nodes[element_id] = {
                "lat": element["lat"],
                "lon": element["lon"]
            }

    ways = []

    # Convert ways to bounding boxes based on their nodes
    for element in raw_buildings["elements"]:
        element_type = element["type"]
        element_id = element["id"]

        if element_type == "way":
            way = [element_id] + get_bounding_box(element, nodes)
            ways.append(way)
    
    return ways


def overpass_find_buildings(task):
    data = """
        [out:json][timeout:25];
        (
        way[building=yes](%s, %s, %s, %s);
        node(w);
        );

        out body;
        >;
    """ % (task["min_lat"], task["min_lon"], task["max_lat"], task["max_lon"])

    r = requests.post("https://overpass.kumi.systems/api/interpreter", data=data)

    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        r.raise_for_status()

def load_tasks_from_file(taskCsv):
    with open(taskCsv, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row
        

def write_polygons_to_csv(project_id, task_id, building_polygons, out):
    for building in building_polygons:
        row = [project_id, task_id] + building
        out.write(",".join([str(r) for r in row]))
        out.write("\n")


def get_output_file(project_id, task_id, output_folder):
    filename = "%s-%s-buildings.csv" % (project_id, task_id)
    path = Path(output_folder)
    path.mkdir(parents=True, exist_ok=True) 
    return path / filename 


def parse_arguments():    
    parser = ArgumentParser() 
    parser.add_argument("-t", "--taskCsv", dest="taskCsv",
                        help="A csv of tasks and their bounding boxes")
    parser.add_argument("-o", "--outputFolder", dest="outputFolder",
                        help="Save results into this folder", default="data/validated_buildings")

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_arguments()

    output_file = None
    out = None
    building_count = 0
    task_count = 0

    for task in load_tasks_from_file(args.taskCsv):
        task_id = task["task_id"]
        project_id = task["project_id"]

        if out is None:
            output_file = get_output_file(project_id, task_id, args.outputFolder)
            out = open(output_file, 'w') 
            out.write("project_id,task_id,way_id,bbox\n")

        print("Looking up buildings for task %s, project %s" % (task_id, project_id))
        raw_buildings = overpass_find_buildings(task)
        building_polygons = convert_to_polygons(raw_buildings)
        
        write_polygons_to_csv(project_id, task_id, building_polygons, out)
        
        building_count = building_count + len(building_polygons)
        task_count = task_count + 1

    if out is not None:
        out.close()
        print("Written %s buildings accross %s tasks to %s" % (building_count, task_count, output_file))

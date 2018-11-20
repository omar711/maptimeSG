from argparse import ArgumentParser
from pathlib import Path

import json
import requests

def get_region_information(textSearch, page = None):
    r = requests.get("https://tasks.hotosm.org/api/v1/project/" + str(projectId))

    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        r.raise_for_status()


def iterate_project_ids(projectJson):
    with open(projectJson, "r") as f:
        projects = json.load(f)

        for project in projects:
            yield project["projectId"]


def get_output_file(projectId, outputFolder):
    filename = str(projectId) + ".json"
    path = Path(outputFolder)
    path.mkdir(parents=True, exist_ok=True) 
    return path / filename 


def parse_arguments():    
    parser = ArgumentParser()
    parser.add_argument("-t", "--textSearch", dest="textSearch",
                        help="Find matching projects containing this text") 
    parser.add_argument("-p", "--projectJson", dest="projectJson",
                        help="Path to JSON file containing project list")
    parser.add_argument("-o", "--outputFolder", dest="outputFolder",
                        help="Save JSON results into this folder", default="data/regions")

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_arguments()

    for projectId in iterate_project_ids(args.projectJson):
        outputFile = get_output_file(projectId, args.outputFolder)

        print("Looking up information for region %s, saving to %s" % (str(projectId), outputFile))
        region = get_region_information(projectId)
        
        with open(outputFile, "w") as out:
            json.dump(region, out)
from argparse import ArgumentParser
from pathlib import Path

import json


"""
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "MultiPolygon",
          "coordinates": [
            [
              [
                [
                  94.7774954283,
                  16.8245079588
                ],
                [
                  94.7774954283,
                  16.8295079588
                ],
                [
                  94.7824954283,
                  16.8295079588
                ],
                [
                  94.7824954283,
                  16.8245079588
                ],
                [
                  94.7774954283,
                  16.8245079588
                ]
              ]
            ]
          ]
        },
        "properties": {
          "taskId": 746,
          "taskX": null,
          "taskY": null,
          "taskZoom": null,
          "taskSplittable": false,
          "taskStatus": "VALIDATED"
        }
      }
"""


def load_region_tasks(regionJson):
    with open(regionJson, "r") as f:
        return json.load(f)


def is_perpendicular(bounding_box):
    """
    Assuming boxes are 'perpendicuar' to the equator. 
    Check each coordinate pair contains one item in common with its previous pair.
    """

    prev_coord = bounding_box[0]
    for coord in bounding_box[1:]:
        if coord[0] != prev_coord[0] and coord[1] != prev_coord[1]:
            return False

        prev_coord = coord
    
    return True


def convert_task_to_row(task):
    coordinates = task["geometry"]["coordinates"]
    bounding_box = coordinates[0][0]

    assert len(bounding_box) is 5, "expected 5 coordinates in bounding box but found %" % bounding_box
    assert bounding_box[0] == bounding_box[4], "expected the first and last coordinates to match: %s - %s" % (bounding_box[0], bounding_box[4])
    assert is_perpendicular(bounding_box), "expected a bounding box perpendicular to the equator, %s" % bounding_box

    min_lat = min([coord[1] for coord in bounding_box])
    min_lon = min([coord[0] for coord in bounding_box])
    max_lat = max([coord[1] for coord in bounding_box])
    max_lon = max([coord[0] for coord in bounding_box])

    taskId = task["properties"]["taskId"]

    return (taskId, min_lat, min_lon, max_lat, max_lon)


def write_tasks_to_csv(out, region):

    validated_tasks = 0
    total_tasks = 0

    out.write("taskId, min_lat, min_lon, max_lat, max_lon\n")

    for task in region["tasks"]["features"]:
        if task["properties"]["taskStatus"] == "VALIDATED":
            validated_tasks = validated_tasks + 1
            
            row = convert_task_to_row(task)
            out.write(",".join([str(r) for r in row]))
            out.write("\n")
        
        total_tasks = total_tasks + 1

    print("Written %s validated tasks out of %s total, to %s" % (validated_tasks, total_tasks, out.name))


def get_output_file(projectId, outputFolder):
    filename = str(projectId) + "-tasks.csv"
    path = Path(outputFolder)
    path.mkdir(parents=True, exist_ok=True) 
    return path / filename 


def parse_arguments():    
    parser = ArgumentParser() 
    parser.add_argument("-p", "--regionJson", dest="regionJson",
                        help="Path to JSON file containing a region's task information")
    parser.add_argument("-o", "--outputFolder", dest="outputFolder",
                        help="Save results into this folder", default="data/validated_tasks")

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_arguments()

    region = load_region_tasks(args.regionJson)

    projectId = region["projectId"]
    outputFile = get_output_file(projectId, args.outputFolder)

    with open(outputFile, 'w') as out:
        write_tasks_to_csv(out, region)

from argparse import ArgumentParser
from pathlib import Path

import json


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


def convert_task_to_row(task, project_id):
    coordinates = task["geometry"]["coordinates"]
    bounding_box = coordinates[0][0]
    task_id = task["properties"]["taskId"]

    if len(bounding_box) != 5:
        print("WARN: skipping (taskId %s): expected 5 coordinates in bounding box but found %s" % (task_id, bounding_box))
        return None

    if not is_perpendicular(bounding_box):
        print("WARN: skipping (taskId %s): expected a bounding box perpendicular to the equator, %s" % (task_id, bounding_box))
        return None
    
    assert bounding_box[0] == bounding_box[4], "(taskId %s): expected the first and last coordinates to match: %s - %s" % (task_id, bounding_box[0], bounding_box[4])

    min_lat = min([coord[1] for coord in bounding_box])
    min_lon = min([coord[0] for coord in bounding_box])
    max_lat = max([coord[1] for coord in bounding_box])
    max_lon = max([coord[0] for coord in bounding_box])

    return (project_id, task_id, min_lat, min_lon, max_lat, max_lon)


def write_tasks_to_csv(out, region, project_id):

    validated_tasks = 0
    total_tasks = 0

    out.write("project_id, task_id, min_lat, min_lon, max_lat, max_lon\n")

    for task in region["tasks"]["features"]:
        if task["properties"]["taskStatus"] == "VALIDATED":
            row = convert_task_to_row(task, project_id)

            if row is not None:
                out.write(",".join([str(r) for r in row]))
                out.write("\n")

                validated_tasks = validated_tasks + 1
        
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

    project_id = region["projectId"]
    outputFile = get_output_file(project_id, args.outputFolder)

    with open(outputFile, 'w') as out:
        write_tasks_to_csv(out, region, project_id)

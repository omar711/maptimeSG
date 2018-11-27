
from argparse import ArgumentParser
from pathlib import Path

import json
import requests

LOCALE = "en"


def search_hot_projects(textSearch):
    page = 1
    json = search_hot_projects_page(textSearch, page)
    hasNext = json["pagination"]["hasNext"]
    results = json["results"]

    while hasNext == True:
        page = page + 1
        json = search_hot_projects_page(textSearch, page)

        hasNext = json["pagination"]["hasNext"]
        results.extend(json["results"])

    return results


def search_hot_projects_page(textSearch, page = None):
    headers = { "Accept-Language" : LOCALE }
    params = { "mapperLevel" : "ALL", "textSearch" : textSearch, "page" : page }
    r = requests.get("https://tasks.hotosm.org/api/v1/project/search", params=params, headers=headers)

    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        r.raise_for_status()


def get_output_file(textSearch, outputFolder):
    filename = textSearch.replace(" ", "_") + ".json"
    path = Path(outputFolder)
    path.mkdir(parents=True, exist_ok=True) 
    return path / filename 


def parse_arguments():    
    parser = ArgumentParser()
    parser.add_argument("-t", "--textSearch", dest="textSearch",
                        help="Find matching projects containing this text") 
    parser.add_argument("-o", "--outputFolder", dest="outputFolder",
                        help="Save JSON results into this folder", default="data/projects")

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_arguments()

    outputFile = get_output_file(args.textSearch, args.outputFolder)
    results = search_hot_projects(args.textSearch)
    print("Found %s matches.  Saving output to %s" % (len(results), outputFile) )

    with open(outputFile, "w") as out:
        json.dump(results, out)

    
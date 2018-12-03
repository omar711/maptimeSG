# Auto-tagging of Buildings

This contains exploratory notes on how we might automatically tag buildings in satellite imagery in order to accelerate work at [hotosm](https://tasks.hotosm.org).  The aim is to decompose this into useful steps and decision points.


# Collecting Training Data

This is where we get started.  It'll require at least a couple of inputs:

1. [Enumerating Projects](wiki/Enumerating-Projects)
1. Validated building polygons
1. Corresponding map tiles from Bing
1. A way to tie the above together: likely via the HOTOSM task database


### Querying Overpass API


## Map tiles


## Validated Areas


## Project Enumeration


# Train a model

This part could get involved.  There are way too many variables in map data to control so we'll have to make many assumptions and constrain the task as far as we can.  

I have many doubts about how far we can get here, but what we have in our favour is that the goal is not to solve the problem outright, but rather to make the task easier and faster for volunteers. 

Options for us:

1. Explore pre-processing of map tiles as this can have a huge effect on algorithm performance
1. Explore various ML models
1. Use multiple models, i.e., an Ayeyarwady-specific model, trained to fit that terrain and architectural style.
1. Use [Kaggle](https://www.kaggle.com/datasets). We could just pose the problem to others by posting a solid dataset to work against. 


# Deployment Options

Once we've made the greatest ever auto-building-tagger, how would it be deployed.  I see the following options, in order of coolness:

1. Run tagger against all unvalidated areas in HOTOSM tasks.  Have these appear as "auto-tagged" areas that require tweaking and validation. 
1. Store models somewhere. Users then run at tagging time, on their own machines, either as:
  1. A browser plugin
  2. A JOSM plugin



# Reading

Here are articles / papers I've spotted that could be promising leads.

1. [Mapping buildings with help from machine learning](https://medium.com/devseed/mapping-buildings-with-help-from-machine-learning-f8d8d221214a): **Note: This is aimed directly at HOTOSM**.  Needs further reading but helping / leeching from them might be a solid option.
1. Microsoft: [Classifying UK Roofs](https://blogs.technet.microsoft.com/uktechnet/2018/04/18/classifying-the-uks-roofs-from-aerial-imagery-using-deep-learning-with-cntk/), plus [source code](https://github.com/TempestVanSchaik/roof-Classification).
1. [Automatic Building Extraction in Aerial Scenes
Using Convolutional Networks](https://arxiv.org/pdf/1602.06564.pdf)
1. [Automatic road tagging](https://wiki.openstreetmap.org/wiki/AI-Assisted_Road_Tracing): very similar workflow and worth reading further when considering how to deploy our work.


# Todos

- [ ] Collection scripts:
  - [x] Enumerate projects, e.g. we will start with the Ayeyarwady Delta
  - [x] Get validated regions via HOT APIs
  - [ ] ~~Handle irregular regions (>5 points in the bounding box)~~
  - [x] Get Bing map tiles for any given region (how many zoom levels?)
    - [ ] Error handling / retry due to connection error making the request in `fetch_and_save_image()`
  - [x] Get building geometry from validated regions
- [ ] Training data:
  - [ ] Overlay building geometry atop Bing tiles
  - [ ] Collect + organise across multiple HOT project areas
- [ ] Machine learning: (for later) 
  - [ ] ...


# Notes on Python Environment

The following should get you started:

```
virtualenv env
source env/bin/activate

pip install jupyter ipython numpy scipy scikit-learn geojson requests opencv-contrib-python matplotlib tqdm

# tensorflow
pip install https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-1.12.0-py3-none-any.whl
pip install tensorflow-hub
```

# Command Line Tools

These live under `scripts/`.  I'll just list basic usage examples for now.  Note there is little in the way of error handling right now. 

## Enumerate Projects

Use this to fetch a list of projects and store away project details for later use.

```
python scripts/enumerate_projects.py  -t Ayeyarwady
Found 40 matches.  Saving output to data/projects/Ayeyarwady.json
```

## Get Region Information

Will fetch region information for every project given as input.  Use the JSON file saved by the `enumerate_projects` tool as input to this.  

Example usage:

```
python scripts/get_project_regions.py -p data/projects/Ayeyarwady.json
Looking up information for region 5364, saving to data/regions/5364.json
.
.
.
Looking up information for region 2469, saving to data/regions/2469.json
```


## Get Validated Task Bounds

Filters a region's tasks to include only `VALIDATED` ones.  Outputs a csv containing `taskId` and a bounding box, expressed as min/max latitude and longitude.

```
python scripts/get_validated_task_bounds.py -p data/regions/2469.json
Written 696 validated tasks out of 886 total, to data/validated_tasks/2469-tasks.csv
```

Example output looks like this:

```
taskId, min_lat, min_lon, max_lat, max_lon
746,16.8245079588,94.7774954283,16.8295079588,94.7824954283
735,16.8345079588,94.7074954283,16.8395079588,94.7124954283
```

This data should guide the subsequent lookup of map tiles.

You can run through a whole directory of project inputs with something like this:

```
for project in `ls -1 data/regions/`; do echo "Project: $project" && python scripts/get_validated_task_bounds.py -p "data/regions/$project"; done

wc -l data/validated_tasks/*
...
14332
```

That means we have 14332 tasks that we can pull data from.  Each should contain many map tiles and many buildings.

## Get Building Geometries per Task

This will find all buildings that lie within the bounding box of any task.  It'll generate a lot. 

Example usage:

```
python scripts/collect_building_geometries.py -t data/validated_tasks/2469-tasks.csv
Looking up buildings for task 746, project 2469
Looking up buildings for task 735, project 2469
.
.
.
Looking up buildings for task 391, project 2469
Written 29247 buildings to data/validated_buildings/2469-746-buildings.csv
```

In this project we have 696 validated tasks so it'll query Overpass 696 times, in each case pulling a list of all 29,247 buildings stored in that task area.  

Once again, you can trawl a whole set of projects using:

```
for project in `ls -1 data/validated_tasks/`; do echo "Project: $project" && python scripts/collect_building_geometries.py -t "data/validated_tasks/$project"; done
```

This is an overnight run, processing all validated tasks from the 40 Ayeyarwady projects we looked up to begin with.  It resulted in output of `545,179` validated building polygons.  The next step is to find the corresponding map tiles.

## Get Map Tiles for Task

This will pull map tiles that cover a given task, at a specified level of zoom.  Usage looks like:

```
python scripts/fetch_bing_tiles.py -t data/validated_tasks/2469-tasks.csv -z 18
Created output folder at data/map_tiles/2469/746/18
Written 20 images to data/map_tiles/2469/746/18
```

The output folder follows the pattern: `{project_id} / {task_id} / {zoom_level}`.  

Similar to above, we can run this for a whole project using:

```
for project in `ls -1 data/validated_tasks/`; do echo "Project: $project" && python scripts/fetch_bing_tiles.py -t "data/validated_tasks/$project" -z 18; done
```

Run this once for each level of zoom we require, which I believe means 17, 18, 19.

Notes: projects `3340, 3744, 3745, 5127` stalled so I terminated. Run this again, zoom level 18.
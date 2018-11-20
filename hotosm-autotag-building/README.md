# Auto-tagging of Buildings

This contains exploratory notes on how we might automatically tag buildings in satellite imagery in order to accelerate work at [hotosm](https://tasks.hotosm.org).  The aim is to decompose this into useful steps and decision points.


# Collecting Training Data

This is where we get started.  It'll require at least a couple of inputs:

1. Validated building polygons
2. Corresponding map tiles from Bing
3. A way to tie the above together: likely via the HOTOSM task database


## Validated Building Polygons

We can use APIs to extract building polygons from OSM, assuming we know the bounding box for a validated area from a HOTOSM task.

### Querying Overpass API

My current best option is the [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API).  

I started out by using an [interactive interpreter](http://overpass-turbo.eu/) so that I could figure out the APIs.  You'll need to focus the map on a suitable area that isn't too large.  I approximated one of the task areas by zooming to an arbitrary part of the Ayeyarwady Delta region.

This is the query I'm using:

```
[out:json][timeout:25];
(
  way[building=yes]({{bbox}});
  node(w);
  
);

out body;
>;
out skel qt;
```

Running the query highlights all buildings within your selected map view and returns data that looks like this:

```
{
  "version": 0.6,
  "generator": "Overpass API 0.7.55.4 3079d8ea",
  "osm3s": {
    "timestamp_osm_base": "2018-11-13T08:55:02Z",
    "copyright": "The data included in this document is from www.openstreetmap.org. The data is made available under ODbL."
  },
  "elements": [

{
  "type": "node",
  "id": 5232934228,
  "lat": 16.1383822,
  "lon": 94.9397551
},

...

{
  "type": "way",
  "id": 541077304,
  "nodes": [
    5232961884,
    5232961885,
    5232961886,
    5232961887,
    5232961884
  ],
  "tags": {
    "building": "yes"
  }
},

...
]
}

```

Each *way* is a building, because I filtered that way in the query above.  The way contains a list of *node*s.  These nodes are also contained in the results and will allow us to transform the list of nodes into a polygon. 

If we can do this automatically, across all validated areas for a particular task (or set of them), we should have a decent set of true data specifying the location of buildings.  The next step would be to pull the relevant imagery from Bing so we can start training machine learning models.


## Map tiles

Grabbing map tiles is usually simple enough.  For example, here is a tile from the Ayeyarwady delta region: 

![tile from the Ayeyarwady delta region](https://ecn.t2.tiles.virtualearth.net/tiles/a1322021130001120320.jpeg?g=587&mkt=en-gb&n=z)

The URL for the tile above is `https://ecn.t2.tiles.virtualearth.net/tiles/a1322021130001120320.jpeg?g=587&mkt=en-gb&n=z`, but note that this might change over time.  

To do this correctly we'll need to use the Bing API.  This [Metadata API](https://msdn.microsoft.com/en-us/library/ff701716.aspx) might be what we need.  It needs testing, and ideally we'd be able to query by bounding box, rather than a centre point.   See also these useful [overview notes on Bing Maps](https://msdn.microsoft.com/en-us/library/bb259689.aspx) themselves.

An API key is needed from [Bing Maps Portal](https://www.bingmapsportal.com).

Here's an example API call that'll return a single tile's metadata, including the image URL:

```
https://dev.virtualearth.net/REST/V1/Imagery/Metadata/Aerial/16.851862450285,95.7293701000399?zl=15&o=json&key=<BING KEY>
```

changing the zoom level gives a series of images:

![Image Tile](http://ecn.t3.tiles.virtualearth.net//tiles//a132201222203023.jpeg?g=6748) ![Image Tile](http://ecn.t2.tiles.virtualearth.net//tiles//a1322012222030232.jpeg?g=6748) ![Image Tile](http://ecn.t1.tiles.virtualearth.net//tiles//a13220122220302321.jpeg?g=6748) ![Image Tile](http://ecn.t1.tiles.virtualearth.net//tiles//a132201222203023211.jpeg?g=6748) ![Image Tile](http://ecn.t1.tiles.virtualearth.net//tiles//a1322012222030232111.jpeg?g=6748)

The challenge here will be identifying the correct set of centre points to create the full grid of map tiles to cover a validated region at our desired zoom level.  I'm sure it's been done elsewhere so some reading is in order.



## Validated Areas

Project details can be retrieved, by project ID, as follows:

```
https://tasks.hotosm.org/api/v1/project/<projectid>
```

For example:

```
https://tasks.hotosm.org/api/v1/project/5364```
```

The response has a lot but interesting to us would be the fields:

* `areaOfInterest`: this contains hundreds of lat/lon pairs. This seems to be a polygon defining the overall shape of the project region.
* `entitiesToMap`: worth checking this includes `buildings`
* `mappingTypes`: array, contains `BUILDINGS`
* **`tasks`**: the big one. 
  * `geometry`: This contains each feature square including box coordinates (5 points, first and last identical)
  * `properties`: contains a `taskStatus`, e.g. `MAPPED`, `VALIDATED`, ... 

I've saved a full [sample JSON file](data/sample/5364-validated-region.json) for the project `5364`.

## Project Enumeration

A quick note on this, currently as a means of collecting relevant project IDs:

```
curl -H "Accept-Language: en" -XGET "https://tasks.hotosm.org/api/v1/project/search?mapperLevel=ALL&textSearch=Ayeyarwady"
```



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


# Todos

- [ ] Collection scripts:
  - [x] Enumerate projects, e.g. we will start with the Ayeyarwady Delta
  - [x] Get validated regions via HOT APIs
  - [ ] Get Bing map tiles for any given region (how many zoom levels?)
    - [ ] Segment region polygon into multiple Bing tile centre points (for suitable zoom levels)
    - [ ] Store tiles using quadkeys for names? Or coords?  These need to correspond neatly to building geometry
  - [ ] Get building geometry from validated regions
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

pip install jupyter ipython numpy scipy scikit-learn geojson requests
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


# Get Validated Task Bounds

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
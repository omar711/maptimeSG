# Machine Tagging of Building Geometry

This contains work toward machine tagging of buildings in satellite imagery to accelerate work of the [Humanitarian OpenStreetMap Team](https://tasks.hotosm.org).  First we will compile a data set suitable for machine learning training, then proceed to learn.  

At a high level, we begin with verified mapping tasks where volunteers have tagged buildings in maps.  A second human later verifies their work.  It is these verified tasks that we collect building polygons and map tiles from.  The image below shows these task areas and their various states of completeness:

<img src="image/irregular-region.png" alt="Verified Task Area" width="400"/>

Once we have verified tasks we can collect building geometry and map tiles.  This involves pulling buildings from OSM and map tiles from Bing.  Below shows a completed state where we have a vanilla map tile (our input) and a tile with labelled buildings in white (our truth).  Together these form the training data for our machine learning pipeline:

<img src="image/map-plus-truth.png" alt="Verified Task Area" width="600"/>

## Collected Data

With a focus on the Ayeyarwady Delta region, we have collected:

* 40 project areas
* 14,292 verified task areas
* 545,139 verified building polygons
* 561,310 (or 7.1GB) corresponding map tiles


# Building the Training Set

We began by compiling a set of training data, along with tools to reproduce this later, or extend for future uses.  The following pages give background on how we collected data from three sources (OSM, HOTOSM, Bing) in order to generate a set of map tiles with corresponding verified building polygons.  

1. [Enumerate Projects of Interest](../../wiki/Enumerating-Projects)
1. [Locate Validated Task Areas](../../wiki/Finding-Validated-Task-Areas)
1. [Query Area for Building Polygons](../../wiki/Find-Building-Polygons-using-the-Overpass-API)
1. [Fetch Map Tiles & Match to Buildings](../../wiki/Find-Map-Tiles-&-Computing-Coordinates)

[Scripts and Code](../../wiki/Data-Collection-Scripts) gives detail on how to set up your environment and then run this data collection process.

In addition you can check out the following Jupyter notebooks for some exploratory work:

1. [Computing Pixel Coordinates to Display Buildings on Map Tiles](scripts/map_tile_truth_preparation.ipynb)

# Machine Learning: Model Training and Deployment

For now I've written very high level notes on [Model Training](../../wiki/Notes-on-Model-Training) and [Deployment Options](../../wiki/Deployment-Options).

I'm also keeping a [Reading List](../../wiki/Reading-List).


# Todos

- [x] Collection scripts:
  - [x] Enumerate projects, e.g. we will start with the Ayeyarwady Delta
  - [x] Get validated regions via HOT APIs
  - [ ] ~~Handle irregular regions (>5 points in the bounding box)~~
  - [x] Get Bing map tiles for any given region (how many zoom levels?)
    - [x] Error handling / retry due to connection error making the request in `fetch_and_save_image()`
  - [x] Get building geometry from validated regions
- [ ] Training data:
  - [ ] Overlay building geometry atop Bing tiles
    - [ ] Iterate over validated building geometries
    - [ ] Lookup maptile in filesystem > draw the corresponding input tile
    - [ ] Think about buildings that cross maptiles
  - [ ] Collect + organise across multiple HOT project areas
- [ ] Machine learning: (for later) 
  - [ ] ...


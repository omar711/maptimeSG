# Machine Tagging of Building Geometry

This contains exploratory notes on how we can machine tag buildings in satellite imagery to accelerate work at [hotosm](https://tasks.hotosm.org).  First we will compile a data set suitable for machine learning training, then proceed to learn.  

At a high level, we begin with verified mapping tasks where volunteers have tagged buildings in maps.  A later human later verifies their work.  It is these verified tasks that we collect building polygons and map tiles from.  The image below shows these task areas and their various states of completeness:

<img src="image/irregular-region.png" alt="Verified Task Area" width="400"/>

Once we have verified tasks we can collect building geometry and map tiles.  This involves pulling buildings from OSM and map tiles from Bing.  Below shows a completed state where we have a vanilla map tile (our input) and a tile labelling buildings in white (our truth).  Together these form the training data for our machine learning pipeline:

<img src="image/map-plus-truth.png" alt="Verified Task Area" width="600"/>


# Collecting Training Data

We begin by compiling a set of training data, along with tools to reproduce this later, or extend for future uses.  The following pages give background on how we collect data from three sources (OSM, HOTOSM, Bing) in order to generate a set of map tiles with corresponding verified building polygons.  

1. [Enumerate Projects of Interest](../../wiki/Enumerating-Projects)
1. [Locate Validated Task Areas](../../wiki/Finding-Validated-Task-Areas)
1. [Query Area for Building Polygons](../../wiki/Find-Building-Polygons-using-the-Overpass-API)
1. [Fetch Map Tiles & Match to Buildings](../../wiki/Find-Map-Tiles-&-Computing-Coordinates)

The scripts and code used to perform this are linked to below.

In addition you can check out the following notebooks for some exploratory work:

1. [Computing Pixel Coordinates to Display Buildings on Map Tiles](scripts/map_tile_truth_preparation.ipynb)

# Machine Learning: Model Training and Deployment

For now I've written very high level notes on [Model Training](../../wiki/Notes-on-Model-Training) and [Deployment Options](../../wiki/Deployment-Options).

I'm also keeping a [Reading List](../../wiki/Reading-List).


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


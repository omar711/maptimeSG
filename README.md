# Machine Tagging of Building Geometry

This contains exploratory notes on how we might automatically tag buildings in satellite imagery in order to accelerate work at [hotosm](https://tasks.hotosm.org).  The aim is to decompose this into useful steps and decision points.


# Collecting Training Data

We begin by compiling a set of training data, along with tools to reproduce this later, or extend for future uses.  The following pages give background on how we collect data from three sources (OSM, HOTOSM, Bing) in order to generate a set of map tiles with corresponding verified building polygons.  

1. [Enumerate Projects of Interest](../../wiki/Enumerating-Projects)
1. [Locate Validated Task Areas](../../wiki/Finding-Validated-Task-Areas)
1. [Query Area for Building Polygons](../../wiki/Find-Building-Polygons-using-the-Overpass-API)
1. [Fetch Map Tiles & Match to Buildings](../../wiki/Find-Map-Tiles-&-Computing-Coordinates)

The scripts and code used to perform this are linked to below.


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


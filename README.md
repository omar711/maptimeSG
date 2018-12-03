# Auto-tagging of Buildings

This contains exploratory notes on how we might automatically tag buildings in satellite imagery in order to accelerate work at [hotosm](https://tasks.hotosm.org).  The aim is to decompose this into useful steps and decision points.


# Collecting Training Data

We begin by compiling a set of training data, along with tools to reproduce this later, or extend for future uses.  The following pages give background on how we collect data from three sources (OSM, HOTOSM, Bing) in order to generate a set of map tiles with corresponding verified building polygons.  

1. [Enumerate Projects of Interest](../../wiki/Enumerating-Projects)
1. [Locate Validated Task Areas](../../wiki/Finding-Validated-Task-Areas)
1. [Query Area for Building Polygons](../../wiki/Find-Building-Polygons-using-the-Overpass-API)
1. [Fetch Map Tiles & Match to Buildings](../../wiki/Find-Map-Tiles-&-Computing-Coordinates)

The scripts and code used to perform this are linked to below.


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

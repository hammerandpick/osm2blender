# Convert any OSM map file to a City in Blender 

## Generating a city from osm map file

* Get the .OSM file from http://openstreetmap.org/ (Search > Export) and store it in %userfolder%/Downloads/map.osm
* Copy and paste the script osm2blender.py in the Text Editor of Blender (See image below)
* Optional: Edit `filepath` to the exact path of .osm file you downloaded in first step.
* Optional: Modify "config" variables for more customization.
  * Scaling in x,y,z direction can be defined
  * If "extrude_not_solidify" is True, this script will extrude existing forms in z-direction otherwise it will solidify the block above the ground element.
  * Some default values can be assigned.
* And Run the script (Text > Run Script)

![screenshot after done](https://raw.githubusercontent.com/mkagenius/osm2blender/master/osm2blender.png)

### Render:

Objects will be linked in collections by streetname and objectname. Objects might be linked in both collections.

[![evee render](https://raw.githubusercontent.com/mkagenius/osm2blender/master/indiranagar_render.png)](https://www.youtube.com/watch?v=3-XonH_mMiU)

#### Note: This is not a perfect script, but it gets something going.



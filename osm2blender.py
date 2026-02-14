from logging import log
import bpy, bmesh

import random

import xml.dom.minidom

import os

# replace filepath with the absolute path of the OSM file you have downloaded
home_directory = os.path.expanduser("~")
print('Searching for map.osm in ' + home_directory)

doc = xml.dom.minidom.parse(home_directory + "/Downloads/map.osm")

# building:levels

all_ways = doc.getElementsByTagName("way")

#prepare collection
osm_collection = bpy.data.collections.new("Import-Collection")
osm_named_buildings_collection = bpy.data.collections.new("Named-Buildings")

# add collection to scene
bpy.context.scene.collection.children.link(osm_collection)
bpy.context.scene.collection.children.link(osm_named_buildings_collection)


buildings = {}
id = 0
latitude = {'minVal':0.0, 'maxVal':0.0, 'startVal':0.0}
longitude = {'minVal':0.0, 'maxVal':0.0, 'startVal':0.0}

for el in all_ways:
    for ch in el.childNodes:
        if ch.attributes:
            if 'k' in ch.attributes.keys() and 'building' ==  ch.attributes['k'].value:
                building_properties = {}
                building_properties['element'] = el
                building_properties['nodes']=[]
                building_properties['name'] = "unknown"
                building_properties['addr:street'] = "unknown"
                building_properties['addr:housenumber'] = "unknown"
                building_properties['roof'] = "flat"
                building_properties['roof_levels'] = 1
                building_properties['height'] = 3.0
                building_properties['levels'] = 1
                building_properties['lat'] = 1.0
                building_properties['lon'] = 1.0
                buildings['id_'+str(id)] = building_properties
                break 
    id += 1

print("Total buildings found: ", len(buildings))

nodes = doc.getElementsByTagName("node")
id_to_tuple = {}
for node in nodes:
    id_val = node.attributes['id'].value
    if 'lon' in node.attributes.keys():
        (lon, lat) = (node.attributes['lon'].value, node.attributes['lat'].value)
        id_to_tuple[id_val] = (lon, lat)

def get_lat_lon_extremes():
    global latitude, longitude, buildings
    for b in buildings:
        lat = float(buildings[b]['lat'])
        lon = float(buildings[b]['lon'])
        if latitude['minVal'] == 0 or lat < latitude['minVal']:
            latitude['minVal'] = lat
        if latitude['maxVal'] == 0 or lat > latitude['maxVal']:
            latitude['maxVal'] = lat
        if longitude['minVal'] == 0 or lon < longitude['minVal']:
            longitude['minVal'] = lon
        if longitude['maxVal'] == 0 or lon > longitude['maxVal']:
            longitude['maxVal'] = lon
    
    latitude['startVal'] = (latitude['maxVal'] + latitude['minVal'])/2
    longitude['startVal'] = (longitude['maxVal'] + longitude['minVal'])/2
    print("Latitude extremes: ", latitude)
    print("Longitude extremes: ", longitude)


#all_buildings = []

for b in buildings:
    nds = buildings[b]['element'].getElementsByTagName('nd')
    for ch in nds:
        if ch.tagName == 'nd':
            node_id = ch.attributes['ref'].value
            buildings[b]['nodes'].append(id_to_tuple[node_id])

    tags = buildings[b]['element'].getElementsByTagName('tag')
    buildings[b]['levels'] = 1
    for tag in tags:
        if tag.tagName == 'tag':
            if tag.attributes['k'].value == 'building:levels':
                try:
                    buildings[b]['levels'] = int(tag.attributes['v'].value)
                except:
                    buildings[b]['levels'] = 1
            if tag.attributes['k'].value == 'alt_name':
                try:
                    buildings[b]['name'] = tag.attributes['v'].value
                except:
                    buildings[b]['name'] = "unknown"
            if tag.attributes['k'].value == 'name':
                try:
                    buildings[b]['name'] = tag.attributes['v'].value
                except:
                    buildings[b]['name'] = "unknown"
            if tag.attributes['k'].value == 'addr:street':
                try:
                    buildings[b]['addr:street'] = tag.attributes['v'].value
                except:
                    buildings[b]['addr:street'] = "unknown"
            if tag.attributes['k'].value == 'addr:housenumber':
                try:
                    buildings[b]['addr:housenumber'] = tag.attributes['v'].value
                except:
                    buildings[b]['addr:housenumber'] = "unknown"
            if tag.attributes['k'].value == 'roof:shape':
                try:
                    buildings[b]['roof'] = tag.attributes['v'].value
                except:
                    buildings[b]['roof'] = "flat"
            if tag.attributes['k'].value == 'roof:levels':
                try:
                    buildings[b]['roof_levels'] = int(tag.attributes['v'].value)
                except:
                    buildings[b]['roof_levels'] = 1
            if tag.attributes['k'].value == 'height':
                try:
                    buildings[b]['height'] = int(tag.attributes['v'].value)
                except:
                    buildings[b]['height'] = buildings[b]['levels'] * 3
    
    if not 'building_name' in locals():
        building_name = buildings[b]['name']

    if not 'building_roof' in locals():
        building_name = buildings[b]['roof']
        
    if not 'building_roof' in locals():
        building_roof = buildings[b]['roof']
    
    if not 'building_height' in locals():
        building_height = buildings[b]['levels'] * 3

    buildings[b]['lat'] = buildings[b]['nodes'][0][1]
    buildings[b]['lon'] = buildings[b]['nodes'][0][0]

    
#buildings=sorted(buildings.items(), key=lambda x: x[1]['lon'], reverse=True)

get_lat_lon_extremes()

def get_xy(lon, lat):
    global latitude, longitude
    lon = float(lon)
    lat = float(lat)
    mul = 111.321 * 1000 # meters
    #mul = 111.321 * 1000 * 1000 #mm
    diff_lon = lon - longitude['startVal']
    diff_lat = lat - latitude['startVal']
    return (diff_lon * mul, diff_lat * mul * -1)
     
# Polygons ready, now use it below

all_poly = []
cnt = 0

obs_list = []

for b in buildings:
    cnt+=1
    tmp = []

    for i in buildings[b]['nodes']:
        (x,y) = get_xy(i[0], i[1])
        x/=-100
        z = 0
        y /= 100
        tmp.append((x,y,z))
    h = buildings[b]['height']

    verts = tmp
    bm = bmesh.new()
    for v in verts:
        bm.verts.new((v[0], v[1], 1))
    bm.faces.new(bm.verts)
    
    bm.normal_update()
    
    # Flip normal if required
    for f in bm.faces:
        if f.normal[2] < 0:
            f.normal_flip()    
    
    me = bpy.data.meshes.new("")
    bm.to_mesh(me)
    
    #create a new collection for each new street, if the building has no street, add it to the unknown collection
    
    building_collection = osm_collection
    
    if buildings[b]['addr:street'] in bpy.data.collections:
        building_collection = bpy.data.collections[buildings[b]['addr:street']]
    else:
        building_collection = bpy.data.collections.new(buildings[b]['addr:street'])
        osm_collection.children.link(building_collection)
    
    ob = bpy.data.objects.new("Nr_"+buildings[b]['addr:housenumber']+"_"+buildings[b]['name'], me)
    ob.modifiers.new("Solidify", type='SOLIDIFY')
    ob.modifiers["Solidify"].thickness = h/10
    
    building_collection.objects.link(ob)
    
    # check if building has a name an add it to a custom collection if it has one, otherwise add it to the unknown collection
    if buildings[b]['name'] != "unknown":
        if buildings[b]['name'] in bpy.data.collections:
            building_collection = bpy.data.collections[buildings[b]['name']]
        else:
            building_collection = bpy.data.collections.new(buildings[b]['name'])
            osm_named_buildings_collection.children.link(building_collection)
        building_collection.objects.link(ob)

    # [start] Adding Glow to each object created, comment it out if not needed    
    matName = "Mater"+str(cnt)
    skymaterial = bpy.data.materials.new(matName)
    ob.active_material = skymaterial 
    nodes = skymaterial.node_tree.nodes
    
    nodes.clear()


    # Create needed Nodes
    nodeOut = nodes.new(type='ShaderNodeOutputMaterial')
    nodeEmission = nodes.new(type='ShaderNodeEmission')
    r = g = b = 0
    if cnt % 3 == 0:
        r = 1.0
        g = 0
        b = 0
    elif cnt % 3 == 1:
        r = 0
        g = 0.5
        b = 1
    elif cnt % 3 == 2:
        r = 0.5
        g = 0
        b = 0.5
        
    nodeEmission.inputs['Color'].default_value = (r,g,b,1)
    nodeEmission.inputs['Strength'].default_value = 4
    
    # Link them together
    links = skymaterial.node_tree.links
    linkOut = links.new(nodeEmission.outputs[0], nodeOut.inputs[0])

    # [end] of Adding Glow to each objct created

    copy = ob.copy()
    obs_list.append(copy)
#    if cnt > 7000:
#        break
    
cnt = 1
for ob in obs_list:
    #print("Linking ", cnt)
    cnt+=1
    bpy.context.scene.collection.objects.link(ob)

print ("Finished processing ", cnt, " buildings")
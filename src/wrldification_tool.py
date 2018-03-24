import json #need this for pretty much everything
from pprint import pprint
import os
from fnmatch import fnmatch
import pathlib
from collections import OrderedDict


print("Starting conversion...")

def lookup(dic, key, *keys):
     if keys:
         return lookup(dic.get(key, {}), *keys)
     return dic.get(key)

def wtype_switch(wtype):
    return { #this is a start, may want to make this better
        'Mechanical': 'room',
        'Stairway': 'stairs',
        'Elevator': 'elevator',
        'Hallway': 'hallway',
        'Door': 'door',
        'Escalator': 'escalator',
        'Janitor': 'room',
        'Washroom': 'bathroom',
        'room': 'room',
        'stairs': 'stairs',
        'elevator': 'elevator',
        'hallway': 'hallway',
        'door': 'door',
        'escalator': 'escalator',
        'bathroom': 'bathroom'
    }.get(wtype,'room')

def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

def alter_props(properties_dict):

    properties = {}
    id = None
    wtype = None
    name = None

    for value in properties_dict:
        properties[value] = properties_dict[value]

    try:
        id = str(properties['OBJECTID'])
    except KeyError:
        id = properties['id'] # allows partially processed files

    try:
        wtype = properties['RM_USE_DESC']
        wtype = wtype_switch(wtype)
    except KeyError:
        wtype = properties['type'] # allows partially processed files

    try:
        nameparts = str(properties['BLD_FLR_RM_ID']).split("_")
        name = nameparts[0]+ " " + nameparts[2]
    except KeyError:
        try:
            if isinstance(properties['name'], str) and "Room: " in properties['name']:
                name = properties['name'].replace('Room: ', '')
            else:
                name = properties['name']
        except KeyError:
            pass
    properties = {}
    properties.update({'id': id, 'type': wtype, 'name': name}) # add the new ones
    return properties

root = '.'
pattern = "*.geojson"

for path, subdirs, files in os.walk(root):
    for name in files:
        if fnmatch(name, pattern):
            with open(os.path.join(path, name), 'r') as f:
                data = json.load(f)
                feature_list = data['features']

                for feature_dict in feature_list:
                    properties_dict = feature_dict['properties']
                    properties_dict = alter_props(properties_dict)
                    feature_dict['properties'] = properties_dict # apply changes

                if feature_list[len(feature_list)-1]['properties'].get('type') == 'building_outline':
                    feature_list.insert(0, feature_list.pop(len(feature_list)-1))

            with open(os.path.join(path, name), 'w') as f:
                json.dump(data, f, sort_keys=True, indent=4, separators=(',', ': '))
                pprint('Wrote cleaned file: '+path+'/'+name)

if __name__ == "__main__":
    pass

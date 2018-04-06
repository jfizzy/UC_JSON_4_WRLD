import json #need this for pretty much everything
from pprint import pprint
import os
from fnmatch import fnmatch
import pathlib
from collections import OrderedDict
from enum import Enum


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
        'bathroom': 'bathroom',
        'wall': 'wall',
        'pathway': 'pathway'
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

            if isinstance(wtype, str):
                if wtype == 'bathroom' and name != 'Men\'s Bathroom' and name != 'Women\'s Bathroom':
                    name = 'Bathroom'
                elif wtype == 'elevator':
                    name = 'Elevator'
                elif wtype == 'escalator':
                    name = 'Escalator'
                elif wtype == 'stairs':
                    name = 'Stairs'
                elif wtype == 'hallway':
                    name = None

        except KeyError:
            pass
    properties = {}
    properties.update({'id': id, 'type': wtype, 'name': name}) # add the new ones
    return properties

def order_levels(level_list):
    sorted = []
    for level in level_list:
        if sorted:
            this = LEVELS.get(level['id'].split('Level')[1])
            for i in range(len(sorted)):
                that = LEVELS.get(sorted[i]['id'].split('Level')[1])
                if this < that:
                    sorted.insert(i, level)
                    break
                elif this > that:
                    if i == len(sorted)-1:
                        sorted.append(level)
                        break
                    else:
                        continue
                else:
                    pprint('found the same level twice!!!!')
        else:
            sorted = [level]

    for i in range(len(sorted)):
        sorted[i]['z_order'] = i

    return sorted

def fix_level_names(level_list):
    for level in level_list:
        if 'Level' in level['name']:
            level['name'] = level['name'].split('Level')[1]
        if not ' ' in level['readable_name']:
            if 'Level' in level['readable_name']:
                l = level['readable_name'].split('Level')[1]
                level['readable_name'] = 'Level '+l
    return level_list

root = '.'
geo_pattern = "*.geojson"
json_pattern = '*main.json'

LEVELS = {'B3': 0, 'B2':1, 'B1':2, 'M1':3, 'G1':4, 'G1A':5, '01':6, '01A':7,
          '02':8, '02A':9, '03':10, '03A':11, '04':12, '04A':13, '05':14,
          '05A':15, '06':16, '06A':17, '07':18, '08':19, '09':20, '10':21,
          '11':22, '12':23, 'P1':24, 'P2':25}

for path, subdirs, files in os.walk(root):
    for name in files:
        if fnmatch(name, geo_pattern) and not name.startswith('Path-'):
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

        elif fnmatch(name, json_pattern) and not name.startswith('Path-'):
            with open(os.path.join(path, name), 'r') as f:
                data = json.load(f)
                level_list = data.get('levels')
                level_list = order_levels(level_list) # orders the levels and applies the correct z order

                #get the entrance level
                entrance_index = 1
                for level in level_list:
                    if level['id'] == 'Level01':
                        entrance_index = level['z_order']
                data.update({'entrance_level': entrance_index})

                level_list = fix_level_names(level_list)

            with open(os.path.join(path, name), 'w') as f:
                json.dump(data, f, sort_keys=True, indent=4, separators=(',', ': '))
                pprint('Wrote cleaned main file: '+path+'/'+name)

if __name__ == "__main__":
    pass

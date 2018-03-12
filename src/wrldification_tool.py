import json #need this for pretty much everything
from pprint import pprint

def lookup(dic, key, *keys):
     if keys:
         return lookup(dic.get(key, {}), *keys)
     return dic.get(key)

with open('../test_files/EN_01.geojson', 'r+') as f:
    data = json.load(f)
    print(type(data))
    print(data.keys())
    feature_list = data['features']

    for feature_dict in feature_list:
        print(type(feature_dict))
        properties_dict = feature_dict['properties']
        print(type(properties_dict))
        properties = {}
        for value in properties_dict:
            properties[value] = properties_dict[value]
        pprint(properties)


if __name__ == "__main__":
    print("Running...")

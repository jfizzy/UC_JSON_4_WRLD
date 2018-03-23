import os
from fnmatch import fnmatch
import pathlib
import json
from pprint import pprint


root = '.'
pattern = "*.*json"

for path, subdirs, files in os.walk(root):
    for name in files:
        if fnmatch(name, pattern):
            with open(os.path.join(path, name), 'r+') as f:
                data = json.load(f)
                #pprint(data)
            with open(os.path.join(path, name), 'w') as f:
                json.dump(data, f, sort_keys=True, indent=4, separators=(',', ': '))
                pprint('Wrote cleaned file: '+path+'/'+name)

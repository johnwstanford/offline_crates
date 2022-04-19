#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 16 10:55:58 2022

@author: johnstanford
"""

import json
import os
import requests
import tarfile
import toml

def resolve_dep(name, version, remaining=None, greater_or_equal=True, path='./crates.io-index'):
    
    remaining_p = name if remaining == None else remaining
    
    print(path, remaining_p)
    
    possibilities = []

    for subpath in os.listdir(path):
        full_subpath = os.path.join(path, subpath)
        if remaining_p.startswith(subpath):
            return resolve_dep(name, version, 
                remaining=remaining_p[len(subpath):], 
                greater_or_equal=greater_or_equal, 
                path=full_subpath)
        if name == subpath and os.path.isfile(full_subpath):
            for line in open(full_subpath):
                dep = json.loads(line)
                if dep['vers'].startswith(version) and greater_or_equal:
                    possibilities.append((int(dep['vers'][len(version)+1:]), dep))
                if dep['vers'] == version:
                    return dep

    if len(possibilities) > 0:
        return max(possibilities, key=lambda d: d[0])[1]

TEMP_TAR = 'temp.tar'
CRATES_PATH = './crates'

CRATE = 'serde_json'
VERSION = '1.0.79'

# Fetch the crate
r = requests.get('https://crates.io/api/v1/crates/%s/%s/download'%(CRATE, VERSION))

if r.status_code != 200:
    raise Exception('Unable to retrieve the given crate from crates.io')

# Extract the archive
if os.path.exists(TEMP_TAR):
    print('Removing old temporary TAR file')
    os.remove(TEMP_TAR)
else:
    print('Not necessary to remove old temporary TAR file')

f_temp = open(TEMP_TAR, 'wb')
f_temp.write(r.content)

tar = tarfile.open(TEMP_TAR)

if not os.path.exists(CRATES_PATH):
    os.makedirs(CRATES_PATH)
    
tar.extractall(CRATES_PATH)

# Load the Cargo.toml
manifest = toml.load(open('%s/%s-%s/Cargo.toml'%(CRATES_PATH, CRATE, VERSION)))

print(manifest.keys())
print(manifest['dependencies'])
print(resolve_dep('serde_json', '1.0'))
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 16 10:55:58 2022

@author: johnstanford
"""

import os
import requests
import tarfile
import toml

TEMP_TAR = 'temp.tar'
CRATES_PATH = './crates'

CRATE = 'serde_derive'
VERSION = '1.0.136'

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

print(manifest)
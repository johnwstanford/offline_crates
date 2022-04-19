#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 16 10:55:58 2022

@author: johnstanford
"""

from colorama import Fore, Style

import json
import os
import re
import subprocess as sp
import toml

TEMP_TAR = 'temp.tar'
CRATES_PATH = './crates'

def resolve_dep(name, version, remaining=None, greater_or_equal=True, path='./crates.io-index'):
    
    remaining_p = name if remaining == None else remaining
    
    print(Fore.BLUE + 'RESOLVE %s %s: %s %s'%(name, version, remaining_p, path) + Style.RESET_ALL)

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
                if dep['vers'] == version:
                    return dep
                if dep['vers'].startswith(version) and greater_or_equal:
                    sum_version = 0
                    split_version = dep['vers'][len(version)+1:].split('.')
                    for i, num in enumerate(split_version):
                        try:
                            sum_version += int(num) * pow(1000, len(split_version)-i-1)
                        except:
                            pass
                    possibilities.append((sum_version, dep))

    print(Fore.BLUE + 'RESOLVE %s %s: %i possibilities'%(name, version, len(possibilities)) + Style.RESET_ALL)

    if len(possibilities) > 0:
        return max(possibilities, key=lambda d: d[0])[1]

def download_dep(crate, version):

    proc = sp.run(['cargo', 'download', '%s=%s'%(crate, version), '-x'], cwd=CRATES_PATH, capture_output=True)
    
    m = re.search(r'(?<=Crate\scontent\sextracted\sto\s)[^\s]+', str(proc.stderr, 'utf-8'))


    # Load the Cargo.toml
    cargo_toml = '%s/%s/Cargo.toml'%(CRATES_PATH, m.group(0))
    manifest = toml.load(open(cargo_toml))

    for section in ['dependencies', 'dev-dependencies']:
        if section in manifest:
    
            for k in manifest[section].keys():
                vers = manifest[section][k].pop('version')
                print(manifest[section][k])
                dep = resolve_dep(k, vers)
                if dep == None:
                    print(Fore.RED + 'Unable to resolve %s %s'%(k, vers) + Style.RESET_ALL)
                    manifest[section][k]['path'] = '../%s/%s-%s'%(CRATES_PATH, k, vers)
                    have_dep = os.path.exists('%s/%s-%s'%(CRATES_PATH, k, vers))
                    print(have_dep)
                    if not have_dep:
                        print(Fore.RED + 'Trying to fetch dependencies for %s %s'%(k, vers) + Style.RESET_ALL)
                        download_dep(k, vers)

                else:
                    print(Fore.CYAN + 'Resolve %s %s => %s'%(k, vers, dep['vers']) + Style.RESET_ALL)
                    manifest[section][k]['path'] = '../%s/%s-%s'%(CRATES_PATH, k, dep['vers'])
                    have_dep = os.path.exists('%s/%s-%s'%(CRATES_PATH, k, dep['vers']))
                    print(have_dep)
                    if not have_dep:
                        print(Fore.CYAN + 'Trying to fetch dependencies for %s %s'%(k, vers) + Style.RESET_ALL)
                        download_dep(k, dep['vers'])

    toml.dump(manifest, open(cargo_toml, 'w'))

crate = resolve_dep('serde_json', '1.0')
download_dep(crate['name'], crate['vers'])
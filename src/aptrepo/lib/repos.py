import configparser
import os
from decimal import *

ARGS_TO_CONF = {"architecture": lambda x: ', '.join(x),
                "restrictions": lambda x: ', '.join(x),
                "https": lambda x: "true" if x else "false"}
CONF_TO_ARGS = {"architecture": lambda x: [y.strip() for y in x.split(',')],
                "restrictions": lambda x: [y.strip() for y in x.split(',')],
                "https": lambda x: True if x.lower() == "true" or x.lower() == "yes" else False}

SUPPORTED_EXTENSIONS = [".deb", ".ipk"]

def write_config_file(path, platform, db):
    cp = configparser.ConfigParser()
    cp[platform] = db
    for arg in ARGS_TO_CONF.keys():
        if arg in db:
            cp[platform][arg] = ARGS_TO_CONF[arg](db[arg])
        
    print("Writing default config template to {}".format(configpath))
    with open(configpath, 'w') as f:
        cp.write(f)
        
def load_config_file(path, platform):
    path = os.path.join(path, platform)
    if not os.path.exists(path):
        raise Exception("Configuration File not found: {}".format(path))
    
    cp = configparser.ConfigParser()
    cp.optionxform = str
    cp.read(path)
    db = {}
    for section in cp.sections():
        for key in cp[section]:
            if key in CONF_TO_ARGS:
                db[key] = CONF_TO_ARGS[key](cp[section][key])
                
            else:
                db[key] = cp[section][key]
            
    return db

def count_supported_packages(path, platform):
    rootpath = os.path.join(path, platform)
    count = 0
    for root, dirs, files in os.walk(rootpath):
        # Use regex instead later
        for f in files:
            for se in SUPPORTED_EXTENSIONS:
                if f[-len(se):len(f)] == se:
                    count += 1
            
    return count

def packagelist(path, platform):
    rootpath = os.path.join(path, platform)
    pl = []
    for root, dirs, files in os.walk(rootpath):
        for f in files:
            for se in SUPPORTED_EXTENSIONS:
                if f[-len(se):len(f)] == se:
                    pl.append(f)
                    print(f)
                    
    return pl
                    
                    

def repo_paths(path, platform):
    rootpath = os.path.join(path, platform)
    paths = dict(root=rootpath)
    """
    for root, dirs, files in os.walk(rootpath):
        print("{}, {}, {}".format(root, files, dirs))
        for d in dirs:
            paths[d] = os.path.join(root, d)
    """
    for f in os.listdir(rootpath):
        if os.path.isdir(os.path.join(rootpath, f)):
            paths[f] = os.path.join(rootpath, f)
            
    return paths

def package_space_usage(path, platform):
    rootpath = os.path.join(path, platform)
    count = 0
    for root, dirs, files in os.walk(rootpath):
        # Use regex instead later
        for f in files:
            for se in SUPPORTED_EXTENSIONS:
                if f[-len(se):len(f)] == se:
                    count += os.path.getsize(os.path.join(root, f))
            
    return "{}K".format(Decimal(count / 1024).quantize(Decimal('0.1'), rounding=ROUND_UP))
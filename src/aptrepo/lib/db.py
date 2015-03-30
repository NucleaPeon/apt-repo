"""
Database Connector for apt-repo

TODO: Improve by chunking reads
"""
import shelve
import os

def init_db(path, pkgname, **kwargs):
    write_keys(path, pkgname, **kwargs)
    if kwargs.get('files') is None:
        write_keys(path, pkgname, files={})
        
def write_keys(path, pkgname, **kwargs):
    with shelve.open(os.path.join(path, pkgname, pkgname), writeback=True) as shelf:
        for k, v in kwargs.items():
            shelf[k] = v
            
    return kwargs

def read_keys(path, pkgname, *keys):
    ret = {}
    with shelve.open(os.path.join(path, pkgname, pkgname), 'r') as shelf:
        for k in keys:
            ret[k] = shelf.get(k)
        
    return ret

def keys(path, pkgname):
    keys = []
    with shelve.open(os.path.join(path, pkgname, pkgname), 'r') as shelf:
        keys = list(shelf.keys())
        
    return keys
        
def entire_db(path, pkgname):
    ret = {}
    with shelve.open(os.path.join(path, pkgname, pkgname), 'r') as shelf:
        ret = dict(shelf.items())
        
    return ret

def delete_key(path, pkgname, key):
    try:
        with shelve.open(os.path.join(path, pkgname, pkgname), writeback=True) as shelf:
            del shelf[key]
            
        return True
            
    except KeyError as kE:
        return False
    
def validate_db(path, pkgname):
    try:
        with shelve.open(os.path.join(path, pkgname, pkgname), 'r') as shelf:
            return True
        
    except Exception as E:
        print(E)
        
    return False
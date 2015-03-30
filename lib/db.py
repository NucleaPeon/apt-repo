"""
Database Connector for apt-repo

TODO: Improve by chunking reads
"""
import shelve
import os

def init_db(path, pkgname, **kwargs):
    write_keys(path, pkgname, **kwargs)
        
def write_keys(path, pkgname, **kwargs):
    with shelve.open(os.path.join(path, pkgname), writeback=True) as shelf:
        for k, v in kwargs.items():
            shelf[k] = v

def read_keys(path, pkgname, *keys):
    ret = {}
    with shelve.open(os.path.join(path, pkgname)) as shelf:
        for k in keys:
            ret[k] = shelf[k]
        
    return ret

def keys(path, pkgname):
    with shelve.open(os.path.join(path, pkgname)) as shelf:
        yield shelf.keys()

def delete_key(path, pkgname, key):
    try:
        with shelve.open(os.path.join(path, pkgname), writeback=True) as shelf:
            del shelf[key]
            
        return True
            
    except KeyError as kE:
        return False
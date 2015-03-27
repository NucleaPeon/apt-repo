"""
Database Connector for apt-repo

TODO: Improve by chunking reads
"""
import json, os
APTPKGDB = '.apt-pkg.db'

def init_repo(**kwargs):
    pass

def init_package(path, pkgname, **kwargs):
    update_package(path, pkgname, **kwargs)
        
def read_package(path, pkgname, **kwargs):
    db = {}
    try:
        with open(os.path.join(path, pkgname, APTPKGDB), 'r') as f:
            db = f.read()
            
    except Exception as E:
        print(E)
        
    return json.loads(db)

def update_package(path, pkgname, **kwargs):
    db = kwargs
    try:
        with open(os.path.join(path, pkgname, APTPKGDB), 'w') as f:
            f.write(json.dumps(db, default=str))
            
    except Exception as E:
        print(E)
        
    return db
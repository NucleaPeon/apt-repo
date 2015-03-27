"""
Database Connector for apt-repo

TODO: Improve by chunking reads
"""
import json, os
APTPKGDB = '.apt-pkg.db'

def init_repo(**kwargs):
    pass

def init_package(path, pkgname, **kwargs):
    if os.path.exists(os.path.join(path, pkgname)):
        update_package(os.path.join(path, pkgname), **kwargs)
        
def read_package(path):
    db = json.dumps({})
    if os.path.exists(os.path.join(path, APTPKGDB)):
        with open(os.path.join(path, APTPKGDB), 'r') as f:
            db = f.read()
            
    return json.loads(db)

def update_package(path, **kwargs):
    db = read_package(path)
    files = db.get('files', {})
    if not kwargs.get('files') is None and isinstance(kwargs.get('files'), dict):
        files.update(kwargs['files'])
        
    db.update(kwargs)
    db['files'] = files
    try:
        with open(os.path.join(path, APTPKGDB), 'w') as f:
            f.write(json.dumps(db, default=str))
            
    except Exception as E:
        print(E)
        
    return db
"""
Database Connector for apt-repo

TODO: Improve by chunking reads
"""
import configparser
import os
import sys
import json
from aptrepo.lib.arch import arch
import socket

# Define how configparser values get placed back into python objects here:
LEGEND = {
    'Package': {
        'set_version': lambda x: str(x),
        'provides': lambda x: [y.strip() for y in x.split(',')],
        'directory': lambda x: os.path.join(x),
        'is_essential': lambda x: x.lower() == "true",
        'desc': lambda x: str(x),
        'description': lambda x: [y.strip() for y in x.split(',')],
        'depends': lambda x: [y.strip() for y in x.split(',')],
        'suggests': lambda x: [y.strip() for y in x.split(',')],
        'replaces': lambda x: [y.strip() for y in x.split(',')],
        'section': lambda x: str(x),
        'architecture': lambda x: [y.strip() for y in x.split(',')]
        },
    'Build': {
        'profiles': lambda x: [y.strip() for y in x.split(',')]
        },
    'Override': lambda x, y: {x: y},
    'Files': lambda x, y: {x: y},
    'Control': lambda x, y: {x: y},
    'User': {'author': lambda x: str(x),
             'maintainer': lambda x: [y.strip() for y in x.split(',')],
             'homepage': lambda x: str(x)}
    }

class PackageDB():
    
    PROFILES = ["deb", "opk", "ipk", "tar.gz"]
    SECTIONS = ['Package', 'Build', 'Override', 'Files', 'Control', 'User']
    
    def __init__(self, path, pkgname, **kwargs):
        
        self.pkgname = pkgname
        self.db = {
            'Package': {
                'set_version': kwargs.get('set_version', "0.1"),
                'provides': kwargs.get('provides', [pkgname]),
                'directory': kwargs.get('directory', os.path.abspath(os.getcwd())),
                'is_essential': kwargs.get('is_essential', False),
                'desc': kwargs.get('desc', "No Description Set"),
                'description': kwargs.get('description', ['...']),
                'depends': kwargs.get('depends', []),
                'suggests': kwargs.get('suggests', []),
                'replaces': kwargs.get('replaces', []),
                'section': kwargs.get('section', "misc"),
                'architecture': kwargs.get('architecture', arch())},
            'Build': {'profiles': ['deb']},
            'Override': {k: v for k, v in kwargs.get('override', {}).items()},
            'Files': {k: v for k, v in kwargs.get('files', {}).items()},
            'Control': {k: v for k, v in kwargs.get('control', {}).items()},
            'User': {'author': kwargs.get('author', ""),
                     'maintainer': kwargs.get('maintainer', [socket.gethostname()]),
                     'homepage': kwargs.get('homepage', '')}}
            

        
        # If a database file already exists, overwrite it with saved information
        if os.path.exists(os.path.join(path, pkgname, pkgname)):
            print("\tReading existing database...")
            try:
                self.read(path, pkgname)
                
            except Exception as E:
                print(str(E))
                print("Found configuration file, but it cannot be read")
                
                         
    def write(self):
        config = configparser.ConfigParser()
        config.optionxform = str
        for k, v in self.db.items():
            if not k in config.sections():
                config[k] = {}
                                
            # section key-value pairs
            for key, val in v.items():
                if isinstance(val, list):
                    val = ', '.join(val)
                    
                elif isinstance(val, bool):
                    val = str(val).lower()
                    
                if val is None or not val:
                    val = ''

                config[k][key] = val
                
        with open(os.path.join(self.db['Package']['directory'], 
                               self.pkgname, self.pkgname), 'w') as f:
            
            config.write(f)
            
            
    def update(self, **kwargs):
        if not kwargs.get('profile') is None:
            if not kwargs['profile'] in self.PROFILES:
                sys.stderr.print("Warning: Build Profile {} is not in the list " 
                    "of supported profiles".format(kwargs['profile']))
            
        # Check if kwargs reflects a key in a section in self.db
        for k, v in kwargs.items():
            for s in self.SECTIONS:
                if k in self.db[s] and not v is None:
                    self.db[s][k] = v
    
    def read(self, path, pkgname):
        """ Reads sections found in SECTIONS """
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(os.path.join(path, pkgname, pkgname))
        
        buildprofs = [a.strip() for a in config['Build']['profiles'].split(',')]
        for bp in list(filter(lambda x: not x in self.PROFILES, buildprofs)):
            sys.stderr.write("Warning: Build Profile {} is not in the list of supported "
                "profiles".format(bp))
            
        
        
        for section in self.SECTIONS:
            for key in config[section]:
                if not isinstance(LEGEND[section], dict):
                    self.db[section].update(LEGEND[section](key, config[section][key]))
                
                else:
                    self.db[section][key] = LEGEND[section][key](config[section][key])
                               
    def validate(self):
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(os.path.join(self.db['Package']['directory'], self.pkgname, self.pkgname))
        for s in config.sections():
            if not s in self.SECTIONS:
                print("Failed to validate section {}".format(s))
                return False
            
        return True
    
    def duplicate(self, path, pkgname):
        ''' Includes some refactoring '''
        raise NotImplementedError(__name__)
    
    def json(self):
        return json.dumps(self.db, default=str,
                             sort_keys=True,
                             indent=4,
                             separators=(',', ': ',))
    
    def __str__(self):
        return str(self.db)

def __keys_to_conf__(dbitems, newdb, sections):
    db = newdb.db
    for key, val in dbitems:
        for section in sections:
            if isinstance(db[section], dict):
                db[section].update(dict(key=val))
                break
                
            else:
                if key in db[section]:
                    if isinstance(val, list):
                        val = ', '.join(val)
                        
                    elif isinstance(val, bool):
                        val = str(val) == "True"
                        
                    if val is None or not val:
                        val = ''

                    db[section][key] = val
                    break
                
    return newdb
    
def migrate(old_db_filehandle, newdb):
    """
    Migrate from old Database shelve structure to a JSON in the format of new db structure
    using an instance of PackageDB (newdb)
    """
    if isinstance(newdb, PackageDB):
        return __keys_to_conf__(old_db_filehandle.items(), newdb, newdb.SECTIONS)
    
    else:
        raise ValueError("Migration failed to translate shelve db into new configparser db")
        
    
    

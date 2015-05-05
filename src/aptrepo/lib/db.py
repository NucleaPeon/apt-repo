"""
Database Connector for apt-repo

TODO: Improve by chunking reads
"""
import configparser
import os
import json
from aptrepo.lib.arch import arch
import socket

# Define how configparser values get placed back into python objects here:
LEGEND = {
    'Package': {
        'set_version': lambda x: str(x),
        'provides': lambda x: x.split(','),
        'directory': lambda x: os.path.join(x),
        'is_essential': lambda x: x == "true",
        'desc': lambda x: str(x),
        'description': lambda x: '\n . \n'.join(x.split(' . ')),
        'depends': lambda x: x.split(','),
        'suggests': lambda x: x.split(','),
        'section': lambda x: str(x),
        'architecture': lambda x: x.split(',')
        },
    'Build': {
        'profiles': lambda x: x.split(',')
        },
    'Override': lambda x, y: {x: y},
    'Files': lambda x, y: {x: y},
    'Control': lambda x, y: {x: y},
    'User': {'author': lambda x: str(x),
             'maintainer': lambda x: x.split(','),
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
                'description': kwargs.get('description', ''),
                'depends': kwargs.get('depends', []),
                'suggests': kwargs.get('suggests', []),
                'section': kwargs.get('section', "misc"),
                'architecture': kwargs.get('architecture', arch())},
            'Build': {'profiles': 'deb'},
            'Override': {k: v for k, v in kwargs.get('override', {}).items()},
            'Files': {k: v for k, v in kwargs.get('files', {}).items()},
            'Control': {k: v for k, v in kwargs.get('control', {}).items()},
            'User': {'author': kwargs.get('author', ""),
                     'maintainer': kwargs.get('maintainer', [socket.gethostname()]),
                     'homepage': kwargs.get('homepage', '')}}
            

        
        # If a database file already exists, overwrite it with saved information
        if os.path.exists(os.path.join(path, pkgname, pkgname)):
            print("Reading existing database.")
            self.read(path, pkgname)
                         
    def write(self):
        config = configparser.ConfigParser()
        for k, v in self.db.items():
            if not k in config:
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
        # Check if kwargs reflects a key in a section in self.db
        for k, v in kwargs.items():
            for s in self.SECTIONS:
                if k in self.db[s] and not v is None:
                    self.db[s][k] = v
    
    def read(self, path, pkgname):
        """ Reads sections found in SECTIONS """
        config = configparser.ConfigParser()
        config.read(os.path.join(path, pkgname, pkgname))
        
        for section in self.SECTIONS:
            for key in config[section]:
                if not isinstance(LEGEND[section], dict):
                    self.db[section].update(LEGEND[section](key, config[section][key]))
                    
                else:
                    self.db[section][key] = LEGEND[section][key](config[section][key])
                               
    def validate(self):
        config = configparser.ConfigParser()
        config.read(os.path.join(self.db['Package']['directory'], self.pkgname, self.pkgname))
        for s in config.sections():
            if not s in self.SECTIONS:
                return False
            
        return True
    
    def duplicate(self, path, pkgname):
        ''' Includes some refactoring '''
        print("duplicate db")
    
    def json(self):
        return json.dumps(self.db, default=str,
                             sort_keys=True,
                             indent=4,
                             separators=(',', ': ',))
    
    def __str__(self):
        return str(self.DB_STRUCT)
    
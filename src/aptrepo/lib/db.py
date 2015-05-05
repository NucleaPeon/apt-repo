"""
Database Connector for apt-repo

TODO: Improve by chunking reads
"""
import configparser
import os
import json
from aptrepo.lib.arch import arch
import socket

class PackageDB():
    
    PROFILES = ["deb", "opk", "ipk", "tar.gz"]
    
    def __init__(self, path, pkgname, **kwargs):
        self.DB_STRUCT = {
            'Package' : {
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
            'Build'   : {'profiles': 'deb'},
            'Override': {k: v for k, v in kwargs.get('override', {}).items()},
            'Control' : {k: v for k, v in kwargs.get('control', {}).items()},
            'Files'   : {k: v for k, v in kwargs.get('files', {}).items()},
            'User'    : {'author': kwargs.get('author', ""),
                         'maintainer': kwargs.get('maintainer', [socket.gethostname()]),
                         'homepage': kwargs.get('homepage', '')}
            }
        self.pkgname = pkgname
                         
    def write(self, **kwargs):
        config = configparser.ConfigParser()
        for k, v in self.DB_STRUCT.items():
            config[k] = {}
            for key, val in v.items():
                if key in kwargs:
                    val = kwargs[key]
                
                if isinstance(val, list):
                    val = ', '.join(val)
                    
                elif isinstance(val, bool):
                    val = str(val).lower()
                    
                if val is None or not val:
                    val = ''
                    
                config[k][key] = val
                
        with open(os.path.join(self.DB_STRUCT['Package']['directory'], 
                               self.pkgname, self.pkgname), 'w') as f:
            config.write(f)
    
    def read_db(self, *keys):
        print("read db")
    
    def validate(self):
        print("validate db")
        return True
    
    def duplicate(self, path, pkgname):
        ''' Includes some refactoring '''
        print("duplicate db")
    
    def __str__(self):
        return str(self.DB_STRUCT)
    
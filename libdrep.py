import conf
import os

class Repository():
    
    @staticmethod
    def add(name, path=conf.PATH, distributions=[], 
               components=[], types=[]):
        if not os.path.exists(path):
            os.makedirs(path, 0o777) # Create dirs recursively
            print("Path Created %s" % path)
            
        # Create required directories:
        dirs = {'base': {'dists' : {}}}
    
    
class Package():
    
    @staticmethod
    def add(name, path=conf.PATH):
        if os.path.exists(path):
            os.makedirs(path, 0o777) # Create dirs recursively
            print("Path Created %s" % path)
            
        
        
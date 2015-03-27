import configparser
import os
import sys

CONFIG_PATH = os.path.join(os.sep, 'etc', 'apt-repo', 'globals.cfg')

def configuration_options(section):
    if os.path.exists(CONFIG_PATH):
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)
        return {x: config[section][x] for x in config[section]}

    elif os.path.exists(os.path.join(os.getcwd(), 'globals.cfg')):
        config = configparser.ConfigParser()
        config.read(os.path.join(os.getcwd(), 'globals.cfg'))
        return {x: config[section][x] for x in config[section]}
    
    else:
        sys.stderr.write("Could not find configuration file globals.cfg\n")
        return {}
    

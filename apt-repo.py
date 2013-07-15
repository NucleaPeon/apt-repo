#!/usr/bin/env python3

"""
Python-based debian repository management system

:Description:
    This software project has no affiliation with Debian's apt system.
    
:Copyright:
    (C) 2013 Southern Alberta Institute of technology, Applied Research Radlab
    
:Date:
    July 15 2013
"""

import argparse, sys, os, conf


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Debian Repository Manager',
    prog="apt-repo",
    epilog='Each action that is called: create/delete/add/remove/update ' +
    'has its own subset of commands that can be viewed by calling the incomplete' +
    ' command.')
    
    parser.add_argument('command', nargs=1, help='create/delete/add/remove/update')
    parser.add_argument('--location', '-l', nargs='?', default=os.getcwd(), 
        help='path to directory where repository should be created; will use default repository names if none specified.' + 
        ' Defaults to the currently directory.')
    parser.add_argument('--distribution', '-d', nargs='?', default=conf.DISTRIBUTION, 
        help='comma-separated list of target distributions, such as "wheezy", "precise", or other debian/ubuntu code names.' + 
        ' Defaults to the current distribution')
    parser.add_argument('--archive', '-a', nargs='?', default='stable,unstable,testing,experimental',
        help='comma-separated list of archives, ex: stable, unstable, testing. Defaults to stable, unstable, testing and experimental')
    parser.add_argument('--component', '-c', nargs='?', default='main,non-free,contrib',
        help='comma-separated list of components, ex: main, non-free, contrib. Defaults to main, non-free and contrib.')
        
    parser.add_argument('[package]', nargs='?', 
        help='specify the package for add, remove and update commands')
    args = parser.parse_args()

   
    
    
    
    
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
from subprocess import PIPE, Popen

# Conversion dictionary from common arch names to proper debian repo names.
ARCH={'x86_64': 'amd64', 'x86': 'i386'}

# Init sane non-required default variables in case user does not set them.
origin = 'Unknown'
label = 'Unknown'
import platform
arch = ARCH.get(platform.machine(), 'Unknown')

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
        help='comma-separated list of components, ex: main, non-free, contrib. Defaults to main, non-free and contrib')
    parser.add_argument('--pretend', '-p', action='store_true', help='Go through output, take no actions')
    parser.add_argument('--recreate', '-r', action='store_true', help='Recreate structure even if certain folders exist'
        
    parser.add_argument('[package]', nargs='?', 
        help='specify the package for add, remove and update commands, wildcard * can be used for selecting all items in a folder location')
    args = parser.parse_args()
    command = args.command[0].lower()
    
    if command not in ['create', 'delete', 'add', 'remove', 'update']:
        sys.stderr.write("Error: Unknown command input: %s\n" % (args.command[0]))
        sys.exit(1)
        
    #TODO:
    #           - Create 
    #           - Delete
    #                   - Release file
    #                   - Packages.gz generation
    #                   - Sources.gz generation
    #                   - watch folder and automatically regenerate *.gz files if modified
    #                     there are programs to do this
    #           - Add
    #           - Remove
    #           - Update
    pretend = args.pretend
    
    location = args.location
    print(location)
    distribution = args.distribution.split(',')
    print(distribution)
    archive = args.archive.split(',')
    print(archive)
    component = args.component.split(',')
    print(component)
    
    if command == 'create':
        print(":: Checking Location if exists: %s" % str(os.path.exists(location)))
        print(":: Checking for existing distribution folder structures...")
        distros_exist = []
        distros_create = []
        for distro in distribution:
            exists = os.path.exists(distro)
            distros_exist.append('%s -> %s' % (distro, str(exists)))
            if not exists:
                distros_create.append(distro)
        print(":: \t %s" % (str(distros_exist)))
        if len(distros_create) > 0:
            print(":: \t Distributions to create... %s" % str(distros_create))
            for distro in distros_create:
                if not pretend:
                    os.makedirs(os.path.join(location, distro))
                print(":: Creating distribution folder: %s, Pretend: %s" % (
                    str(os.path.exists(os.path.join(location, distro))), str(pretend)))
                archives_exist = []
                archives_create = []
                print(':: Checking for existing archive folder structures...')
                for arc in archive:
                    exists = os.path.exists(arc)
                    archives_exist.append('%s -> %s' % (arc, str(exists)))
                    if not exists:
                        archives_create.append(arc)
                print(":: \t %s" % str(archives_exist))
                if len(archives_create) > 0:
                    print(":: \t Archive to create... %s" % str(archives_create))
                    for arc in archives_create:
                        if not pretend:
                            os.makedirs(os.path.join(location, distro, arc))
                        print(":: Creating archive %s in distribution %s, Pretend: %s" % (
                            str(arc), str(distro), str(pretend)))
                        comps_exist = []
                        comps_create = []
                        print(":: Checking for existing component folder structures...")
                        for comp in component:
                            exists = os.path.exists(comp)
                            comps_exist.append('%s -> %s' % (comp, str(exists)))
                            if not exists:
                                comps_create.append(comp)
                        print(":: \t %s" % str(comps_exist))
                        if len(comps_create) > 0:
                            print(":: \t Component to create... %s" % str(comps_create))
                            for comp in comps_create:
                                if not pretend:
                                    os.makedirs(os.path.join(location, distro, arc, comp))
                                    releasefile = open(os.path.join(location, distro, arc, comp, 'Release'), 'w')
                                    releasefile.write('''Archive: %s\nComponent: %s\nOrigin: %s\nLabel: %s\nArchitecture: %s''' %
                                                      (arc, comp, origin, label, arch))
                                    releasefile.close()
                                print(":: Creating component %s in archive %s in distribution %s, Pretend: %s" % (
                                    comp, arc, distro, pretend))
                                print(":: Creating Release File")
                                
def generate_release_file(archive, component, origin=origin, label=label, arch=arch):
    '''
    :Description:
        Creates the Release file, a short text file with a description of the
        repo. If arguments are not supplied for origin, label, and arch, a
        best guess is made for arch and "Unknown" is set for the former two.
        
        Parameters arhive and component are automatically assigned when folders
        are being created. 
    :Parameters:
        - archive: string; examples: quantal, wheezy, precise
        - component: string; examples: stable, unstable, testing, experimental
        - origin: string; your company name
        - label: string; your repository name
        - arch: string; architecture of the repo. Default value is current pc 
                architecture

    :Returns:
        - None: method creates and generates release file. Will overwrite if
                called twice
    '''
    pass

#!/usr/bin/env python3

"""
Python-based debian repository management system

:Description:
    This software project has no affiliation with Debian's Official apt system.
    
    Manages and automates a repository with emphasis on the greatest ease of
    automation and control.
    
    :create:
        By default, this creates a repository in the current directory with 
        defaults for a stable main repository. FIXME: Default to current dist
        codename.

:Copyright:
    (C) 2015 PeonDevelopments
    (C) 2015 Angry Coders Inc.
"""

import argparse, sys, os, platform
import datetime
import platform
import logging


from subprocess import PIPE, Popen
from __init__ import arch_dir, get_arch

def ini_section_header(properties_file, header_name):
    yield '[{}]\n'.format(header_name)
    for line in properties_file:
        yield line
        
ACTIONS = ["create", "delete", "info", "add", "remove", "source"]

if __name__ == "__main__":
    '''
    TODO:
        --secure (full secure apt repository, auto configure gpg)
        
    '''

    # --> Start Command Line Argument parsing
    parser = argparse.ArgumentParser(description="Debian Repository Management Tool")
    parser.add_argument('action',
                       help="one of: create, delete, status, add, remove, info")
    parser.add_argument('--desc', nargs='?', default="(description goes here)", 
                        help="Set a repository description")
    parser.add_argument('--directory', '-d', default=os.path.join(os.getcwd(), "foo"), nargs='?',
                        help="Sets the top level directory for filesystem repositories")
    parser.add_argument('--name', '-n', nargs='?', default=None,
                        help="Sets the account name of the repository")
    parser.add_argument('--email', '-e', nargs=1, default="no-reply@localhost.com", 
                        help="Sets the account email address")
    parser.add_argument('--ip', '-i', nargs=1, help="Overrides the auto ip discovering feature")
    parser.add_argument('--gpg', '-g', nargs=1, default=None, #"./apt-repo.public.key",
                        help="Exports (and optionally creates) the gpg key to target path and filename")
    parser.add_argument('--architecture', '-a', nargs="*", default=[get_arch(platform.machine())],
                        help="Architectures to create repository with; defaults to current arch and source")
    parser.add_argument('--toplevel', '-t', nargs="?", default='debian',
                        help="name of top level directory; defaults to 'debian'")
    parser.add_argument('--platforms', '-f', nargs="*", default=['stable'], #'unstable', 'testing'],
                        help="Platforms to support; defaults to 'stable'. Codenames are preferred"
                        "Other official platforms are 'experimental' and '*/updates (stable/updates), etc.")
    parser.add_argument('--restrictions', '-r', nargs="*", default=["main"],
                         help="Package Freedom Restrictions (main, contrib, non-free), defaults to 'main'")
    parser.add_argument('--https', '-s', action="store_true", default=False,
                        help="Sets the apt address to https instead of http")
    parser.add_argument('--verbosity', '-v', nargs='?', default=0, help="Output program calls to stdout")
    # TODO: --force (on add and remove actions, create and delete (respectively) the components that would 
    #                otherwise make it fail.)
    
    args = parser.parse_args()
    # <-- End Command Line Argument parsing

    # --> Start managing cli arguments to produce an Action
    nix_platform = platform.linux_distribution() # (name, id,)
    
    # Catches all invalid actions and exists the program so we can avoid validation later.
    action = args.action.lower()
    if not action in ACTIONS:
        sys.stderr.write("Invalid action: {}.\nAvailable actions: {}\n".format(
            action, ', '.join(ACTIONS)))
        sys.exit(1)
        
    path = os.path.join(args.directory, args.toplevel, 'dists')
    
    if action == "create":
        print("::Create\n")
        umask = os.umask(0o022)
        for x in args.restrictions:
            os.makedirs(os.path.join(args.directory, args.toplevel, 'pool', x),
                        exist_ok=True)
        # Ugly 3x for loop, let's be straight forward and append all unique paths
        os.makedirs(path, exist_ok=True)
        print([get_arch(a) for a in args.architecture])
        with open(os.path.join(path, 'Release'), 'w') as f:
            f.write("Origin: {}\n".format(args.name))
            f.write("Label: {}\n".format(args.name))
            f.write("Suite: {}\n".format('wheezy'))
            f.write("Codename: {}\n".format('wheezy')) # FIXME
            f.write("Date: {}\n".format(datetime.datetime.strftime(datetime.datetime.now(), "%a, %d %b %Y %H:%M:%S %Z")))
            f.write("Architectures: {}\n".format(' '.join([get_arch(a) for a in args.architecture])))
            f.write("Components: {}\n".format(' '.join(args.restrictions)))
            f.write("Description: {}\n".format(args.desc))
            f.write("MD5Sum:\n  {}".format('\n  '.join([])))

#        with open(os.path.join(path, 'Release.gpg'), 'w') as f:
#            f.write("")

        #for z in args.architecture:
            #with open(os.path.join(path, 'Contents-{}'.format(get_arch(z))), 'w') as f:
                #pass

        for x in args.platforms:
            for y in args.restrictions:
                for z in args.architecture:
                    os.makedirs(os.path.join(path, x, y, arch_dir(z)),
                                exist_ok=True)
                    with open(os.path.join(path, x, y, arch_dir(z), "Release"), 'w') as f:
                        f.write("Archive: {}\n".format(x))
                        f.write("Origin: {}\n".format(args.name))
                        f.write("Label: {}\n".format(args.name))
                        f.write("Component: {}\n".format(y))
                        f.write("Architecture: {}\n".format(get_arch(z)))
                        #f.write("Version: 0.1\n")

    elif action == "delete":
        print("::Delete\n")
        umask = os.umask(0o022)
        import shutil
        print("\tRemoving {}".format(args.directory))
        if os.path.exists(args.directory):
            shutil.rmtree(os.path.join(args.directory))
            
        else:
            sys.stderr.write("Error: Failed to remove non-existant directory: {}\n".format(
                args.directory))
            sys.exit(2)
        
    elif action == "info":
        '''
        INFO:
            - List all the packages that exist in the components specified in the arguments
            - List each component of the repository that exists
            - List total stats of each repo section
            - List the ip address of the repo, list the deb line for the sources file
        '''
        import json
        if os.path.exists(path):
            import socket
            # TODO: valid={check if repo structure works}
            print(json.dumps(dict(ipaddr=socket.gethostbyname(socket.gethostname()),
                                  filepath=os.path.abspath(path),
                                  apt="deb http{}://{}/{} {} {}".format("s" if args.https else "",
                                      socket.gethostbyname(socket.gethostname()), args.toplevel, ' '.join(args.platforms),
                                      ' '.join(args.restrictions)),
                                  architectures=args.architecture,
                                  platforms=args.platforms,
                                  contribs=args.restrictions,
                                  webserverroot=os.path.abspath(os.path.join(args.directory, args.toplevel))), 
                             default=str,
                             sort_keys=True,
                             indent=4,
                             separators=(',', ': ',)))
    
    elif action == "source":
        '''
        SOURCE:
            - Output the line(s) in debian source .list format based on components specified in arguments
        '''
        pass
    
    elif action == "add":
        # Adds a component to an existing repo.
        pass
    
    elif action == "remove":
        pass
            

    # <-- Action has been performed, if successful we exit with 0 status
    sys.exit(0)

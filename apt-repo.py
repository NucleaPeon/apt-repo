#!/usr/bin/env python3

"""
Python-based debian repository management system

:Description:
    This software project has no affiliation with Debian's Official apt system.
    
    Manages and automates a repository with emphasis on the greatest ease of
    automation and control.
    
    This program aims to do as much as possible for the user and automate all
    the small details so the user doesn't have to worry about them. Automate
    gpg and hashes, update them whenever an update is called for, create
    files for all possible scenarios whenever possible -- always create 
    options for source, even if it isn't used.
    
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
import socket
import hashlib
import shutil
import json
from lib.scanpackages import Packages_gz

from subprocess import PIPE, Popen
from __init__ import arch_dir, get_arch
        
def repo_path_validate(base, platforms, restrictions):
    # Returns True if valid, False otherwise
    return not False in repo_paths(base, platforms, restrictions)

def repo_paths(base, platforms, restrictions):
    all_paths = []
    for p in platforms:
        all_paths.extend([os.path.join(base, p, r) for r in restrictions])
    
    return all_paths
        
ACTIONS = ["create", "delete", "modify", "info", "add", "remove", "export", "gpg", "haspkg", "help"]

if __name__ == "__main__":
    '''
    TODO:
        Write Release files with md5sum on Packages{.gz} and Sources{.gz} if applicable
        
    '''
    
    # --> Declare all methods to reuse code here:
    def format_deb_line(ip, platforms, restrictions, https=False):
        return "deb http{}://{}/ {} {}".format("s" if https else "", ip, 
                                                 ' '.join(platforms), ' '.join(restrictions))

    # FIXME: This needs to be moved into the lib folder so it can be shared with
    #        apt-pkg, which also needs to update files as packages are tracked.

    def md5sum_file(path, filename):
        f = os.path.join(path, filename)
        if not os.path.exists(f):
            raise Exception("Attempted to generate hash of file {}, file not found".format(f))
        
        md5 = hashlib.md5()
        with open(f, 'r') as openf:
            md5.update(openf.read().encode("utf-8")) # FIXME: Read in at 128 bytes so we don't overload on huge files
        
        filesize = os.stat(f).st_size
        # format and return it
        # FIXME: we may need to buffer and right-align the filesize for readability and standization
        return " {}\t{} {}".format(md5.hexdigest(), filesize, filename) 

    def gen_gpg_key():
        proc = Popen(["gpg", "--gen-key", "--batch"])
        proc.communicate()
        
    
    # <-- End Method Declarations

    # --> Start Command Line Argument parsing
    parser = argparse.ArgumentParser(description="Debian Repository Management Tool")
    parser.add_argument('action', nargs='*',
                       help="Run 'apt-repo help' to list all the actions")
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
                        help="Exports (and optionally creates) the gpg key to target path and filename") # TODO: Confirm use case of this option
    parser.add_argument('--architecture', '-a', nargs="*", default=[get_arch(platform.machine())],
                        help="Architectures to create repository with; defaults to current arch and source")
    parser.add_argument('--toplevel', '-t', nargs="?", default='debian',
                        help="name of top level directory; defaults to 'debian'")
    parser.add_argument('--platforms', '-f', nargs="*", default=['stable'], #'unstable', 'testing'],
                        help="Platforms to support; defaults to 'stable'. Codenames are preferred"
                        "Other official platforms are 'experimental' and '*/updates (stable/updates), etc.")
    parser.add_argument('--restrictions', '-r', nargs="*", default=["main"],
                         help="Package Freedom Restrictions (main, contrib, non-free), defaults to 'main'")
    parser.add_argument('--https', '-s', action="store_true", default=False, # FIXME: This should also take the server key as param to deploy
                        help="Sets the apt address to https instead of http")
    parser.add_argument('--verbosity', '-v', nargs='?', default=0, help="Output program calls to stdout")
    # TODO: --force (on add and remove actions, create and delete (respectively) the components that would 
    #                otherwise make it fail.)
    
    args = parser.parse_args()
    # <-- End Command Line Argument parsing

    # --> Start managing cli arguments to produce an Action
    nix_platform = platform.linux_distribution() # (name, id,)
    
    # Catches all invalid actions and exists the program so we can avoid validation later.
    action = args.action[0].lower()
    if not action in ACTIONS:
        sys.stderr.write("Invalid action: {}.\nAvailable actions: {}\n".format(
            action, ', '.join(ACTIONS)))
        sys.exit(1)
        
    path = os.path.join(args.directory, args.toplevel, 'dists')
    getlist = lambda: repo_paths(path, args.platforms, args.restrictions)
    
    if action == "create":
        umask = os.umask(0o022)
        for x in args.restrictions:
            os.makedirs(os.path.join(args.directory, args.toplevel, 'pool', x),
                        exist_ok=True)
        # Ugly 3x for loop, let's be straight forward and append all unique paths
        os.makedirs(path, exist_ok=True)
        
        # Before the Release file is created, we need the following files to be created and filled out. TODO
        # RESEARCH THIS NOW
        
        relfiles = ["Packages", "Packages.gz", "Sources", "Sources.gz"]
        with open(os.path.join(path, 'Release'), 'w') as f:
            f.write("Origin: {}\n".format(args.name))
            f.write("Label: {}\n".format(args.name))
            f.write("Suite: {}\n".format('wheezy'))
            f.write("Codename: {}\n".format('wheezy')) # FIXME
            f.write("Date: {}\n".format(datetime.datetime.strftime(datetime.datetime.now(), "%a, %d %b %Y %H:%M:%S %Z")))
            f.write("Architectures: {}\n".format(' '.join([get_arch(a) for a in args.architecture])))
            f.write("Components: {}\n".format(' '.join(args.restrictions)))
            f.write("Description: {}\n".format(args.desc))
            f.write("MD5Sum:\n")
            for x in relfiles:
                if os.path.exists(os.path.join(path, x)):
                    f.write(" {}\n".format(md5sum_file(path, x)))
                    
        # IMPORTANT! GNU GPG requires some work going on in order to generate entropy
        # This is a stop-gap for an important step.

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
                        
    elif action == "modify":
        # Change attributes in Release files or add/remove arches, platforms or restrictive components
        print("TODO")

    elif action == "delete":
        umask = os.umask(0o022)
        
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
        
        if os.path.exists(path):
            # TODO: valid={check if repo structure works}
            pkgs = {}
            for x in getlist():
                for a in args.architecture:
                    pkgdir = os.path.join(x, arch_dir(a))
                    pkgs[pkgdir] = [ f for f in os.listdir(pkgdir) if os.path.isfile(os.path.join(pkgdir, f)) and ".deb" in f ]
                    
            print(pkgs)
            print(json.dumps(dict(ipaddr=socket.gethostbyname(socket.gethostname()),
                                  filepath=os.path.abspath(path),
                                  apt=format_deb_line(socket.gethostbyname(socket.gethostname()),
                                                      args.platforms, args.restrictions, https=args.https),
                                  architectures=args.architecture,
                                  platforms=args.platforms,
                                  packagecount={r: len(pkgs[r]) for r in pkgs},
                                  contribs=args.restrictions,
                                  valid=repo_path_validate(path, args.platforms, args.restrictions),
                                  webserverroot=os.path.abspath(os.path.join(args.directory, args.toplevel))), 
                             default=str,
                             sort_keys=True,
                             indent=4,
                             separators=(',', ': ',)))
    
    elif action == "add":
        # Adds a component to an existing repo.
        packages = args.action[1:]
        modifiedrepos = []
        if packages:
            for p in packages:
                if len(p) > 4 and p[-4:] == ".deb":
                    for rpath in getlist():
                        # Seperate package from path
                        newp = p.split(os.sep)[-1]
                        for arch in args.architecture:
                            rpath = os.path.join(rpath, arch_dir(arch))
                            shutil.copyfile(p, os.path.join(rpath, newp)) # No metadata copied, need to chown and chmod?
                            if not rpath in modifiedrepos:
                                modifiedrepos.append(rpath) 
                            print("Copying {} to {}".format(p, os.path.join(rpath, arch_dir(arch), newp)))
                            
        if modifiedrepos:
            for mr in modifiedrepos:
                Packages_gz(mr)
    
    elif action == "remove":
        modifiedrepos = []
        packages = args.action[1:]
        if packages:
            for rpath in getlist():
                for a in args.architecture:
                    modified = False
                    files = [ f for f in os.listdir(os.path.join(rpath, arch_dir(a))) if f[-4:] == ".deb" ]
                    for f in files:
                        # we compare the debian package name, omit the version and arch string which should be standard.
                        # We also check for verbatim comparisons
                        splt = f.split('-')
                        for foundpkg in filter(lambda x: '-'.join(splt[0:len(splt)-1]) == x, packages):
                            os.remove(os.path.join(rpath, arch_dir(a), f))
                            modified = True
                            print("Found {}, Removing {} from {}".format(foundpkg, f, os.path.join(rpath, arch_dir(a))))
                            
                        for foundpkg in filter(lambda x: x == f, packages):
                            os.remove(os.path.join(rpath, arch_dir(a), f))
                            modified = True
                            print("Removing {}".format(os.path.join(rpath, arch_dir(a), foundpkg)))
                            
                    if modified:
                        modifiedrepos.append(rpath)
                            
        if modifiedrepos:
            for mr in modifiedrepos:
                Packages_gz(mr)
        
    elif action == "haspkg":
        # Initialize search results
        # NOTE: This complex code can be eliminated with the introduction of a database
        pkgs = {}
        pkglist = []
        for x in getlist():
            for a in args.architecture:
                pkgdir = os.path.join(x, arch_dir(a))
                pkgs[pkgdir] = []
                pkglist = [ f for f in os.listdir(pkgdir) if os.path.isfile(os.path.join(pkgdir, f)) and ".deb" in f ]
                for pkg in args.action[1:]:
                    for p in pkglist:
                        pkg = pkg.replace('.deb', '')
                        # Add package if the string is found in the name and if it isn't already added
                        if pkg in p:
                            if not p in pkgs[pkgdir]:
                                pkgs[pkgdir].append(p)
                
        print(json.dumps(pkgs, default=str, sort_keys=True,
                             indent=4, separators=(',', ': ',)))
    
    elif action == "export":
        for p in args.platforms:
            print(format_deb_line(socket.gethostbyname(socket.gethostname()),
                                  [p], args.restrictions, https=args.https))
            
        # TODO: Source repository names
        
    elif action == "gpg":
        # Here we might want to automatically create some work (fibinocchi sequence?)
        # while generating the key.
        # This generates the key how Debian would prefer it to be generated
        gen_gpg_key()
        
    elif action == "help":
        print()
        print("apt-repo program help")
        print("=====================")
        print()
        print("apt-repo is a repository-focused script that allows automation of admin tasks.")
        print("The following are actions that can be performed:")
        print()
        print("create: Creates the repository directory structure and all the necessary files")
        print("        in it to enable the user to connect to, and subsequently update from,")
        print("        an empty repository.")
        print()
        print("        Relevant Options:")
        print("        \to --directory (Specify where to create repository structure")
        print("        \to --desc (Set the Release file description")
        print("        \to --name (Sets the Release account name of the repository)")
        print("        \to --email (Sets the Release email account, usually maintainers'")
        print("        \to --architecture (Create directories for the specified ")
        print("                            architectures")
        print("        \to --toplevel (Top level directory is the suffix to the deb")
        print("                        sources.list")
        print("        \t              line, defaults to 'debian')")
        print("        \to --platforms (Create directories that separate packages")
        print("                         based on stability)")
        print("        \to --restriction (Create directories for free/non-free/")
        print("                           contrib packages.")
        print()
        print("delete: Removes the repository directory structure completely")
        print("        Relevant Options:")
        print()
        print("        \to --directory (Specify where repository is to remove)")
        print()
        print("modify: Adds or removes certain components to the repository, such as")
        print("        architectures, platforms, and package restrictions (non-free)")
        print()
        print("        \to --architecure")
        print("        \to --platforms")
        print("        \to --restrictions")
        print("        \to --name")
        print("        \to --email")
        print("        \to --desc")
        print("        \to --directory")
        print("        \to --toplevel")
        print()
        print("gpg:    Generates the gpg key. For now, let's assume the user can ")
        print("        create their own, as entropy and environment are important")
        print("        for the creation of a good key.")
        print()
        print("info:   ")
        print()
        print("add:   ")
        print()
        print("remove:   ")
        print()
        print("haspkg:   ")
        print()
            

    # <-- Action has been performed, if successful we exit with 0 status
    sys.exit(0)
    

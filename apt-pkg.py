#!/usr/bin/env python3

"""
Python-based debian package management system

:Description:
    This software project has no affiliation with Debian's Official apt system.

:Copyright:
    (C) 2015 PeonDevelopments
    (C) 2015 Angry Coders Inc.
"""

import argparse, sys, os, platform
import datetime
from subprocess import PIPE, Popen
from __init__ import arch_dir, get_arch

ACTIONS = ["create", "delete", "modify", "update", "build", "valid", "info", "licenses", "sections", "help"]

SECTIONS = ["admin", "cli-mono", "comm", "database", "debug", "devel", "doc", "editors", "education", "electronics", 
    "embedded", "fonts", "games", "gnome", "gnu-r", "gnustep", "graphics", "hamradio", "haskell", "httpd", "interpreters", "introspection",
    "java", "kde", "kernel", "libdevel", "libs", "lisp", "localization", "mail", "math", "metapackages", "misc", "net",
    "news", "ocaml", "oldlibs", "otherosfs", "perl", "php", "python", "ruby", "science", "shells", "sound", "tasks",
    "tex", "text", "utils", "vcs", "video", "web", "x11", "xfce", "zope"]
# NOTE: Anytime a package is updated, it must update the gpg file

def update_pkg(package_name):
    """
    :Description:
        Take all the steps to update the target debian folder package data
        - Update Install-Size
        - Regenerate control file
        - Re-validate package data
    """
    pass

if __name__ == "__main__":

    # --> Start Command Line Argument parsing
    parser = argparse.ArgumentParser(description="Apt Package Management Tool")
    # publish command when invoked as the primary action will read in the transaction file
    # of commands made (add, remove) in chronological order so users can see their changes
    # before they are made live. Config file options can make this automatic, or supply --publish
    # option (-p) to each package command
    parser.add_argument('action', nargs="*",
                       help="Perform an action: create, delete, modify, update, build, valid, info, licenses, help")
    parser.add_argument('--directory', '-d', nargs=1, default=os.getcwd(),
                        help="Specify directory to host debian package data")
    parser.add_argument('--author', nargs='*', 
                        help='Sets the name of the package author(s). Use format "author name <author@email.com>"')
    parser.add_argument('--architecture', '-a', nargs="*", default=[get_arch(platform.machine()), 'all'],
                        help="Architectures to create repository with; defaults to current arch and source")
    parser.add_argument('--section', nargs=1, default="misc", 
                        help="Specify section for package to be added to. Run 'apt-pkg sections' for list")
    parser.add_argument('--essential', action="store_true", default=False
                        help="Specify this arg to make the package essential. Default is False.")
    parser.add_argument('--depends', nargs="*", help="List package names that this package depends on.",
                        default=[])
    parser.add_argument('--recommends', nargs="*", help="List package names that this package recommends.",
                        default=[])
    
    parser.add_argument('--license', '-l', nargs=1, help="Specify license to associate with package")
    parser.add_argument('--set-version', nargs=1, help="Set the version string for all packages to this",
                        default="0.1")
    args = parser.parse_args()
    # <-- End Command Line Argument parsing
    action = args.action[0].lower()
    
    if not action in ACTIONS:
        sys.stderr.write("Invalid action: {}.\nAvailable actions: {}\n".format(
            action, ', '.join(ACTIONS)))
        sys.exit(1)

    if action == "create":
        for pkgname in args.action[1:]:
            print(pkgname)
            umask = os.umask(0o022)
            os.makedirs(os.path.join(args.directory, pkgname, "DEBIAN"), exist_ok=True)
            # Create control file with any data we have to work with:
            with open(os.path.join(args.directory, pkgname, "DEBIAN", "control"), 'w') as cf:
                cf.write("Package: {}\n".format(pkgname))
                cf.write("Version: {}\n".format(args.set_version))
                cf.write("Architecture: {}\n".format(args.architecture))
                cf.write("Section: {}\n".format(args.section if args.section in SECTIONS else "misc"))
                cf.write("Essential: {}\n".format("yes" if args.essential else "no"))
                cf.write("Depends: {}\n".format(', '.join(args.depends)))
                cf.write("Recommends: {}\n".format(', '.join(args.recommends)))
                '''
                Recommends: # comma-separated-value
                Suggests: # csv
                Provides: spartacus- # generic package (ex: spartacus-db)
                Homepage: http://www.angrycoders.com
                Built-Using: python (>= 3.4)
                Package-Type: deb
                Maintainer: Daniel Kettle <daniel.kettle@angrycoders.com>
                Description: Configuration Component of Spartacus
                This
                is 
                a
                .
                detailed
                description
                in
                .
                the proper format.
                )
                '''
        
    elif action == "sections":
        print('\n'.join(SECTIONS))
    
    elif action == "help":
        print()
        print("apt-pkg program help")
        print("====================")
        print()
        print("apt-repo is a repository-focused script that allows automation of admin tasks.")
        print("The following are actions that can be performed:")
        print()
        print("create: Creates the directory structure for the specified package names.")
        print("        Package names should generally not include version numbers and should")
        print("        only consist of characters, digits and hyphens. Defaults to 'all' arch")
        print("        Names cannot start with digits.")
        print()
        print("delete: ")
        print()
        print("modify: ")
        print()
        print("update: ")
        print()
        print("build:  ")
        print()
        print("valid:  ")
        print()
        print("info:   ")
        print()
        print("licenses: ")
        print()
            
        

    sys.exit(0)

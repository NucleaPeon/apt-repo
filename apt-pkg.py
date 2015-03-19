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
import socket
import shutil
from subprocess import PIPE, Popen
from __init__ import arch_dir, get_arch

ACTIONS = ["create", "delete", "modify", "update", "build", "valid", "info", "licenses", "sections", "help", None]

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

def pkg_installed_size(path, append_bytes=None):
    """
    :Description:
        Recursive method that aims to compile a total Installed-Size value
        for the resulting control file.
        Performs a quick check to ensure the DEBIAN folder is not included.
    """
    bytecount = 0
    if os.path.exists(path):        
        if os.path.isdir(path):
            files = os.listdir(path)
            for f in files:
                if f.upper() == "DEBIAN" and os.path.exists(os.path.join(path, f, 'control')) \
                    and os.path.isfile(os.path.join(path, f, 'control')):
                    continue
                
                f = os.path.join(path, f)
                bytecount += pkg_installed_size(f) if os.path.isdir(f) else os.path.getsize(f)
            
        else:
            bytecount += os.path.getsize(path)
    
    return bytecount

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
    parser.add_argument('--architecture', '-a', nargs=1, default=get_arch(platform.machine()),
                        help="Architectures to create repository with; defaults to current arch and source")
    parser.add_argument('--section', nargs=1, default="misc", 
                        help="Specify section for package to be added to. Run 'apt-pkg sections' for list")
    parser.add_argument('--essential', action="store_true", default=False,
                        help="Specify this arg to make the package essential. Default is False.")
    parser.add_argument('--depends', nargs="*", help="List package names that this package depends on.",
                        default=[])
    parser.add_argument('--recommends', nargs="*", help="List package names that this package recommends.",
                        default=[])
    parser.add_argument('--suggests', nargs="*", help="List package names that this package recommends.",
                        default=[])
    parser.add_argument('--provides', nargs="*", 
                        help="If you set the provides for a package list, its size must equal the number " 
                        "of package names supplied to create action.")
    parser.add_argument('--built-using', nargs='*',
                        help="If you set the built-using for a package list, its size must equal the number " 
                        "of package names supplied to create action. use empty quotes for packages where " 
                        "this doesn't apply")
    parser.add_argument('--maintainer', nargs=1, help="Set the maintainer(s) for all packages in format: " 
                        "'full name <email@this.com>'", default=socket.gethostname())
    parser.add_argument('--homepage', nargs=1, help="Set the homepage in the control file.")
    parser.add_argument('--license', '-l', nargs=1, help="Specify license to associate with package")
    parser.add_argument('--set-version', nargs=1, help="Set the version string for all packages to this",
                        default="0.1")
    parser.add_argument('--desc', nargs=1, help="Set the description summary")
    parser.add_argument('--description', nargs='*', help="Set the full description, each line should "
                        "be surrounded in quotes and supplied to this parameter. Ex: " 
                        "--description 'this is a long' 'description of my package'", default=[])
    args = parser.parse_args()
    # <-- End Command Line Argument parsing
    action = args.action[0].lower() if len(args.action) > 0 else None
    
    if not action in ACTIONS:
        sys.stderr.write("Invalid action: {}.\nAvailable actions: {}\n".format(
            action, ', '.join(ACTIONS)))
        sys.exit(1)

    if action == "create":
        for i, pkgname in enumerate(args.action[1:]):
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
                if args.depends:
                    cf.write("Depends: {}\n".format(', '.join(args.depends)))
                    
                if args.recommends:
                    cf.write("Recommends: {}\n".format(', '.join(args.recommends)))
                
                if args.suggests:
                    cf.write("Suggests: {}\n".format(', '.join(args.suggests)))
                
                cf.write("Provides: {}\n".format(pkgname if not args.provides else args.provides[i]))
                cf.write("Installed-Size: {}\n".format(pkg_installed_size(os.path.join(args.directory, pkgname))))
                if args.homepage:
                    cf.write("Homepage: {}\n".format(args.homepage))
                cf.write("Package-Type: deb\n")
                if args.maintainer:
                    cf.write("Maintainer: {}\n".format(args.maintainer))
                    
                cf.write("Description: {}\n".format(args.desc))
                for d in args.description:
                    cs.write(" {}\n".format(d))
                    
        
    elif action == "delete":
        for a in args.action[1:]:
            d = os.path.join(args.directory, a)
            if os.path.exists(d) and os.path.isdir(d):
                # Do a quick check for package confirmation
                if os.path.isfile(os.path.join(d, "DEBIAN", "control")):
                    umask = os.umask(0o022)
                    print("Removing {} Package".format(d))
                    shutil.rmtree(d)
                    
                else:
                    print("Not a Debian Package folder")
                    sys.exit(4)
                    
            else:
                sys.stderr.write("Error: Failed to remove non-existant directory: {}\n".format(
                    args.directory))
                sys.exit(2)
        
    elif action == "sections":
        print('\n'.join(SECTIONS))
        
    elif action == "licenses":
        print()
        print("       [main licenses]")
        print("          - GNU General Public License")
        print("          - GNU Lesser General Public License")
        print("          - GNU Library General Public License")
        print("          - Modified BSD License")
        print("          - Perl Artistic License")
        print("          - Apache License")
        print("          - Expat/MIT-style License")
        print("          - zlib-style License")
        print("          - LaTeX Public Project License")
        print("          - Python Software Foundation License")
        print("          - Ruby's License")
        print("          - PHP License")
        print("          - W3C Software Notice and License")
        print("          - OpenSSL License")
        print("          - Sleepycat License")
        print("          - Common Unix Printing System License Agreement")
        print("          - vhf Public License")
        print("          - \"No problem Bugroff\" License")
        print("          - Unmodified BSD License")
        print("          - public domain")
        print("          - IBM Public License Version 1.0")
        print()
        print("       [non-free licenses]")
        print("          - NVIDIA Software License")
        print("          - SCILAB License")
        print("          - Limited Use Software License Agreement")
        print("          - Non-Commercial License")
        print("          - FastCGI / Open Market License")
        print("          - LaTeX2HTML License")
        print("          - Open Publication License")
        print("          - Free Document Dissemination License")
        print("          - AT&T Open Source License")
        print("          - Apple Public Source License")
        print("          - Aladdin Free Public License")
        print("          - Generic amiwm License (an XV-style license)")
        print("          - Digital License Agreement")
        print("          - Moria/Angband License")
        print("          - Unarj License")
        print("          - id Software License")
        print("          - qmail terms")
        print()
    
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

    elif action is None:
        sys.exit(3)
        

    sys.exit(0)

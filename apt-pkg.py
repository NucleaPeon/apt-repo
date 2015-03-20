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

# local apt-repo modules
from __init__ import arch_dir, get_arch
from lib.build import build_package

ACTIONS = ["create", "delete", "modify", "add", "remove", "update", "build", "valid", "info", "licenses", "sections", "help", None]

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

def has_deb_structure(path):
    if os.path.exists(path) and os.path.isdir(path):
        for f in os.listdir(path):
            if f.upper() == "DEBIAN":
                testfile = os.path.join(path, f, "control")
                return os.path.isfile(testfile) and os.path.exists(testfile)
            
    return False

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
                if has_deb_structure(os.path.join(path, f, 'control')):
                    continue
                
                f = os.path.join(path, f)
                bytecount += pkg_installed_size(f) if os.path.isdir(f) else os.path.getsize(f)
            
        else:
            bytecount += os.path.getsize(path)
    
    return bytecount

def write_into(src, dst, overwrite=True, symlinks=False):
    toplevel = src.split(os.sep)[-1]
    target = os.path.join(dst, toplevel)
    if not os.path.exists(target):
        shutil.copytree(src, target, symlinks=symlinks)
    
    else:
        subtarget = target # Initialize before reuse
        print("Directory {} exists...".format(subtarget))
        for dirpath, dirnames, filenames in os.walk(src):
            for dname in dirnames:
                subtarget = os.path.join(dst, toplevel, dirpath.split(toplevel)[-1].lstrip(os.sep), dname)
                if not os.path.exists(subtarget):
                    shutil.copytree(os.path.join(dirpath, dname), subtarget, symlinks=symlinks)
                
                else:
                    print("Directory {} exists...".format(subtarget))
            
            for fname in filenames:
                subtarget = os.path.join(dst, toplevel, dirpath.split(toplevel)[-1].strip(os.sep), fname)
                if not os.path.exists(subtarget) or overwrite:
                    shutil.copy2(os.path.join(dirpath, f), subtarget, follow_symlinks=symlinks)
                    
                else:
                    print("File {} exists...".format(subtarget))
                    
def remove_from(dst, name, remove_all=False, find_dirs=True, find_files=True):
    name = name.split(os.sep)[-1]
    retval = False
    for dirpath, dirnames, filenames in os.walk(dst):
        if find_files:
            if name in filenames:
                print("Found {} in filenames".format(name))
                rem = os.path.join(dirpath, name)
                os.remove(rem)
                retval = True
                if remove_all:
                    continue
                
                else:
                    break
            
        if find_dirs:
            if name in dirnames:
                print("Found {} in dirnames".format(name))
                rem = os.path.join(dirpath, name)
                shutil.rmtree(rem)
                retval = True
                if remove_all:
                    continue
                
                else:
                    break
            
        else:
            continue
        
    return retval
            
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
    parser.add_argument('--follow-symlinks', action="store_true", help="Allow symlinks to be added into packages",
                         default=False)
    parser.add_argument('--overwrite', action="store_false", default=True,
                        help="Overwrite files when adding to a package, enabled by default.")
    args = parser.parse_args()
    # <-- End Command Line Argument parsing
    action = args.action[0].lower() if len(args.action) > 0 else None
    
    def write_control_file(packagename, iteration=0):
        umask = os.umask(0o022)
        # Create control file with any data we have to work with:
        with open(os.path.join(args.directory, packagename, "DEBIAN", "control"), 'w') as cf:
            cf.write("Package: {}\n".format(packagename))
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
            
            cf.write("Provides: {}\n".format(packagename if not args.provides else args.provides[iteration]))
            cf.write("Installed-Size: {}\n".format(pkg_installed_size(os.path.join(args.directory, packagename))))
            if args.homepage:
                cf.write("Homepage: {}\n".format(args.homepage))
            cf.write("Package-Type: deb\n")
            if args.maintainer:
                cf.write("Maintainer: {}\n".format(args.maintainer))
                
            cf.write("Description: {}\n".format(args.desc))
            for d in args.description:
                cs.write(" {}\n".format(d))
    
    if not action in ACTIONS:
        sys.stderr.write("Invalid action: {}.\nAvailable actions: {}\n".format(
            action, ', '.join(ACTIONS)))
        sys.exit(1)

    if action == "create":
        for i, pkgname in enumerate(args.action[1:]):
            umask = os.umask(0o022)
            d = os.path.join(args.directory, pkgname)
            
            if not os.path.exists(d):
                print("Creating {} Package".format(pkgname))
                os.makedirs(os.path.join(d, "DEBIAN"), exist_ok=True)
                write_control_file(pkgname, i)
                
            else:
                sys.stderr.write("Warning: Package {} exists. Skipping...\n".format(pkgname))
                continue
        
    elif action == "delete":
        for a in args.action[1:]:
            d = os.path.join(args.directory, a)
            if os.path.exists(d) and os.path.isdir(d):
                # Do a quick check for package confirmation
                if has_deb_structure(d):
                    umask = os.umask(0o022)
                    print("Removing {} Package".format(d))
                    shutil.rmtree(d)
                    
                else:
                    sys.stderr.write("Warning: Not a Debian Package folder\n")
                    
                    
            else:
                sys.stderr.write("Warning: Directory {} does not exist.\n".format(
                    args.directory))
                sys.exit(2)
        
    elif action == "modify":
        print("TODO: Go through arguments and modify ones that have changed, or rewrite")
        
    elif action == "add":
        if len(args.action) < 2:
            sys.stderr.write("No files are being added to {}\n".format(
                args.action[1]))
            sys.exit(5)
            
        copypath = os.path.join(args.directory, args.action[1])
        if not has_deb_structure(copypath):
            sys.stderr.write("Not a recognized debian package directory: {}\n".format(
                args.action[1]))
            sys.exit(6)
        
        for a in args.action[2:]:
            write_into(a, copypath)
            write_control_file(args.action[1])
        
    elif action == "remove":
        if len(args.action) < 2:
            sys.stderr.write("No files specified to be removed from {}\n".format(
                args.action[1]))
            sys.exit(5)
        
        for a in args.action[2:]:
            print("removing {} from {}".format(a, os.path.join(args.directory, args.action[1])))
            result = remove_from(os.path.join(args.directory, args.action[1]), a)
            if not result:
                sys.stderr.write("Warning: Could not find file or directory {} in {}\n".format(a, args.action[1]))
        
    elif action == "build":
        for a in args.action[1:]:
            d = os.path.join(args.directory, a)
            if has_deb_structure(d):
                retcode = build_package(d)
                if not retcode == 0:
                    sys.stderr.write("Error: Package Building Failed, control file may be bad")
                    # TODO: more information
                    sys.exit(7)
                
            else:
                sys.stderr.write("Warning: {} is not a debian package directory.\n".format(d))
        
    elif action == "update":
        print("rescan package folder for updates and persist them in relevant files")
        
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

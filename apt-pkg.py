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

ACTIONS = ["create", "delete", "modify", "update", "build", "valid", "info", "licenses", "help"]
# NOTE: Anytime a package is updated, it must update the gpg file

if __name__ == "__main__":

    # --> Start Command Line Argument parsing
    parser = argparse.ArgumentParser(description="Apt Package Management Tool")
    # publish command when invoked as the primary action will read in the transaction file
    # of commands made (add, remove) in chronological order so users can see their changes
    # before they are made live. Config file options can make this automatic, or supply --publish
    # option (-p) to each package command
    parser.add_argument('action', nargs="*",
                       help="Perform an action: create, delete, modify, update, build, valid, info, licenses, help")
    parser.add_argument('--author', nargs='*', 
                        help='Sets the name of the package author(s). Use format "author name <author@email.com>"')
    parser.add_argument('--architecture', '-a', nargs="*", default=[get_arch(platform.machine()), 'source'],
                        help="Architectures to create repository with; defaults to current arch and source")
    parser.add_argument('--license', '-l', nargs=1, help="Specify license to associate with package")
    args = parser.parse_args()
    # <-- End Command Line Argument parsing
    action = args.action[0].lower()
    
    if not action in ACTIONS:
        sys.stderr.write("Invalid action: {}.\nAvailable actions: {}\n".format(
            action, ', '.join(ACTIONS)))
        sys.exit(1)

    

    sys.exit(0)

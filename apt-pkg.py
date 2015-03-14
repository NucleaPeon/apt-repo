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
from __init__ import archdir, ARCH

def arch(architecture):
    '''
    :Description:
        Translates non-debian compliant arch strings to compliant ones

    :Parameters:
        architecture string: name of arch (amd64 / x86_64)

    :Returns:
        string properly formatted architecture
        Example: "x86_64" ==> "amd64", "x86" >> "i386"
    '''
    return ARCH.get(architecture, architecture)

def ini_section_header(properties_file, header_name):
    yield '[{}]\n'.format(header_name)
    for line in properties_file:
        yield line

if __name__ == "__main__":

    # --> Start Command Line Argument parsing
    parser = argparse.ArgumentParser(description="Apt Repository Management Tool")
    # publish command when invoked as the primary action will read in the transaction file
    # of commands made (add, remove) in chronological order so users can see their changes
    # before they are made live. Config file options can make this automatic, or supply --publish
    # option (-p) to each package command
    parser.add_argument('action',
                       help="[repo]: create, delete, status [package]: add, remove, info, publish")
    parser.add_argument('--desc', nargs='?', default="", help="Set a repository description")
    parser.add_argument('--simple', action="store_true", default=True,
                        help="(Default) [create] Writes a simple repo file structure")
    parser.add_argument('--directory', '-d', default=os.path.join(os.getcwd(), "foo"), nargs='?',
                        help="Sets the top level directory for filesystem repositories")
    parser.add_argument('--name', '-n', nargs='?', default="Debian",
                        help="Sets the account name of the repository")
    parser.add_argument('--email', '-e', nargs=1, help="Sets the account email address")
    parser.add_argument('--ip', '-i', nargs=1, help="Overrides the auto ip discovering feature")
    parser.add_argument('--gpg', '-g', nargs=1, default="./apt-repo.public.key",
                        help="Exports (and optionally creates) the gpg key to target path and filename")
    parser.add_argument('--publish', '-p', action="store_true",  default=False,
                        help="When accompanying a package command, performs the command")
    parser.add_argument('--architecture', '-a', nargs="*", default=[platform.machine(), 'source'],
                        help="Architectures to create repository with; defaults to current arch and source")
    parser.add_argument('--toplevel', '-t', nargs="?", default='debian',
                        help="name of top level directory; defaults to 'debian'")
    parser.add_argument('--platforms', '-f', nargs="*", default=['stable', 'unstable', 'testing'],
                        help="Platforms to support; defaults to 'stable', 'unstable' and 'testing'. "
                        "Other official platforms are 'experimental' and '*/updates (stable/updates), etc.")
    parser.add_argument('--package-restrictions', '-r', nargs="*", default=["main"],
                         help="Package Freedom Restrictions (main, contrib, non-free), defaults to 'main'")
    args = parser.parse_args()
    # <-- End Command Line Argument parsing
    

    sys.exit(0)

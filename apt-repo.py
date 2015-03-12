#!/usr/bin/env python3

"""
Python-based debian repository management system

:Description:
    This software project has no affiliation with Debian's Official apt system.

    # TODO: Chain argparse objects together so we can better organized help and
    #       understanding of the software (repo-based, package-based) or split
    #       package and repo commands into different files: apt-repo, apt-pkg

:Copyright:
    (C) 2015 PeonDevelopments
"""

import argparse, sys, os, platform
import datetime
from subprocess import PIPE, Popen


ARCH = {"x86_64": "amd64",
        "x86": "i386"}

def archdir(architecture):
    if architecture != "source":
        return "binary-{}".format(arch(architecture))

    return arch(architecture)

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

    simple = True

    # First set up argument parsing, then compile and overwrite
    # with config arguments if found

    '''
        --add-local (adds the entry into your /etc/apt/sources.list.d/ folder with the local fs path instead of external)
        --simple (default, creates the dir structure and files for easy public access)
        --secure (full secure apt repository, mutually exclusive with --simple)
    '''

    parser = argparse.ArgumentParser(description="Apt Repository Management Tool")
    # publish command when invoked as the primary action will read in the transaction file
    # of commands made (add, remove) in chronological order so users can see their changes
    # before they are made live. Config file options can make this automatic, or supply --publish
    # option (-p) to each package command
    parser.add_argument('action',
                       help="[repo]: create, delete, status [package]: add, remove, info publish")
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

    if args.action.lower() == "create":
        print("Create")
        print(args)
        umask = os.umask(0o022)
        for x in args.package_restrictions:
            os.makedirs(os.path.join(args.directory, args.toplevel, 'pool', x),
                        exist_ok=True)
        # Ugly 3x for loop, let's be straight forward and append all unique paths
        path = os.path.join(args.directory, args.toplevel, 'dists')
        os.makedirs(path)
        with open(os.path.join(path, 'Release'), 'w') as f:
            f.write("Origin: {}\n".format(args.name))
            f.write("Label: {}\n".format(args.name))
            f.write("Suite: {}\n".format('wheezy'))
            f.write("Codename: {}\n".format('wheezy')) # FIXME
            f.write("Date: {}\n".format(datetime.datetime.strftime(datetime.datetime.now(), "%a, %d %b %Y %H:%M:%S %Z")))
            f.write("Architectures: {}\n".format(' '.join([arch(a) for a in args.architecture])))
            f.write("Components: {}\n".format(' '.join(args.package_restrictions)))
            f.write("Description: {}\n".format(args.desc))
            f.write("MD5Sum:\n  {}".format('\n  '.join([])))

        with open(os.path.join(path, 'Release.gpg'), 'w') as f:
            f.write("")

        for z in args.architecture:
            with open(os.path.join(path, 'Contents-{}'.format(arch(z))), 'w') as f:
                pass



        for x in args.platforms:
            for y in args.package_restrictions:
                for z in args.architecture:
                    os.makedirs(os.path.join(path, x, y, archdir(z)),
                                exist_ok=True)
                    with open(os.path.join(path, x, y, archdir(z), "Release"), 'w') as f:
                        f.write("Archive: {}\n".format(x))
                        f.write("Origin: {}\n".format(args.name))
                        f.write("Label: {}\n".format(args.name))
                        f.write("Component: {}\n".format(y))
                        f.write("Architecture: {}\n".format(arch(z)))
                        #f.write("Version: 0.1\n")

        #TODO: ^^^ Check for existing Release file

        with open(os.path.join(args.directory, args.toplevel, "aptftp.conf"), 'w') as f:
            #TODO: Find out how multiple architectures and suites and components are defined
            f.write("APT::FTPArchive::Release {\n")
            f.write("  Origin \"{}\";\n".format(args.name))
            f.write("  Label \"{}\";\n".format(args.name))
            f.write("  Suite {};\n".format(' '.join(["\"{}\"".format(x) for x in args.platforms])))
            # Codename: "sid"
            f.write("  Architectures {};\n".format(' '.join(["\"{}\"".format(x) for x in args.architecture])))
            f.write("  Components {};\n".format(' '.join(["\"{}\"".format(x) for x in args.package_restrictions])))
            f.write("  Description \"Public Archive for {}\";\n".format(args.name))
            f.write("};")

        with open(os.path.join(args.directory, args.toplevel, "aptgenerate.conf"), 'w') as f:
            f.write("Dir::ArchiveDir \".\";\n")
            f.write("Dir::CacheDir \".\";\n")
            f.write("TreeDefault::Directory \"pool/\";\n")
            f.write("TreeDefault::SrcDirectory \"pool/\";\n")
            f.write("Default::Packages::Extensions \".deb\";\n")
            f.write("Default::Packages::Compress \". gzip bzip2\";\n")
            f.write("Default::Sources::Compress \"gzip bzip2\";\n")
            f.write("Default::Contents::Compress \"gzip bzip2\";\n")

            for x in args.platforms:
                for y in args.package_restrictions:
                    for z in args.architecture:
                        if z != "source":
                            f.write("BinDirectory \"dists/unstable/main/binary-amd64\" {\n")
                            f.write("  Packages \"dists/{}/{}/{}/Packages\";\n".format(x, y, 'binary-' + z)) # binary-amd64, not just amd64
                            f.write("  Contents \"dists/{}/Contents-{}\";".format(x, 'Contents-' + z)) # amd64 only
                            f.write("  SrcPackages \"dists/{}/{}/source/Sources\";\n".format(x, y))
                            f.write("};\n")

    sys.exit(0)

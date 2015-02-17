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
from subprocess import PIPE, Popen


ARCH = {"x86_64": "amd64",
        "x86": "i386"}

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
    parser.add_argument('args', nargs='+', help="Types of repositories to make or package names specified")
    parser.add_argument('--simple', action="store_true", default=True,
                        help="(Default) [create] Writes a simple repo file structure")
    parser.add_argument('--directory', '-d', default=os.path.join(os.getcwd(), "foo"), nargs='?',
                        help="Sets the top level directory for filesystem repositories")
    parser.add_argument('--name', '-n', nargs=1, help="Sets the account name of the repository")
    parser.add_argument('--email', '-e', nargs=1, help="Sets the account email address")
    parser.add_argument('--ip', '-i', nargs=1, help="Overrides the auto ip discovering feature")
    parser.add_argument('--gpg', '-g', nargs=1, default="./apt-repo.public.key",
                        help="Exports (and optionally creates) the gpg key to target path and filename")
    parser.add_argument('--publish', '-p', action="store_true",  default=False,
                        help="When accompanying a package command, performs the command")
    parser.add_argument('--architecture', '-a', nargs="?", default=platform.machine(),
                        help="Architecture to create, defaults to current system arch")
    args = parser.parse_args()
    print(args.args)


    if args.action.lower() == "create":
        print("Create")
        print(args)
        umask = os.umask(0o022)
        print(umask)
        print(args.directory)
        os.makedirs(os.path.join(args.directory, 'debian', 'pool', 'main'),
                    exist_ok=True)
        os.makedirs(os.path.join(os.path.join(args.directory, 'debian', 'dists', *args.args), 'source'),
                    exist_ok=True)
        os.makedirs(os.path.join(os.path.join(args.directory, 'debian', 'dists', *args.args), "binary-{}".format(
            arch(args.architecture))), exist_ok=True)

    sys.exit(0)
'''
Create an archive tree called "Origin: Foo" as the following.

$ umask 022
$ mkdir -p ~/public_html/debian/pool/main
$ mkdir -p ~/public_html/debian/dists/unstable/main/binary-amd64
$ mkdir -p ~/public_html/debian/dists/unstable/main/source
$ cd ~/public_html/debian
$ cat > dists/unstable/main/binary-amd64/Release << EOF
Archive: unstable
Version: 4.0
Component: main
Origin: Foo
Label: Foo
Architecture: amd64
EOF
$ cat > dists/unstable/main/source/Release << EOF
Archive: unstable
Version: 4.0
Component: main
Origin: Foo
Label: Foo
Architecture: source
EOF
$ cat >aptftp.conf <<EOF
APT::FTPArchive::Release {
  Origin "Foo";
  Label "Foo";
  Suite "unstable";
  Codename "sid";
  Architectures "amd64";
  Components "main";
  Description "Public archive for Foo";
};
EOF
$ cat >aptgenerate.conf <<EOF
Dir::ArchiveDir ".";
Dir::CacheDir ".";
TreeDefault::Directory "pool/";
TreeDefault::SrcDirectory "pool/";
Default::Packages::Extensions ".deb";
Default::Packages::Compress ". gzip bzip2";
Default::Sources::Compress "gzip bzip2";
Default::Contents::Compress "gzip bzip2";

BinDirectory "dists/unstable/main/binary-amd64" {
  Packages "dists/unstable/main/binary-amd64/Packages";
  Contents "dists/unstable/Contents-amd64";
  SrcPackages "dists/unstable/main/source/Sources";
};

Tree "dists/unstable" {
  Sections "main";
  Architectures "amd64 source";
};
EOF
You can automate repetitive updates of APT archive contents on your server system by configuring dupload.

Place all package files into "~foo/public_html/debian/pool/main/" by executing "dupload -t foo changes_file" in client while having "~/.dupload.conf" containing the following.

$cfg{'foo'} = {
  fqdn => "www.example.com",
  method => "scpb",
  incoming => "/home/foo/public_html/debian/pool/main",
  # The dinstall on ftp-master sends emails itself
  dinstall_runs => 1,
};

$cfg{'foo'}{postupload}{'changes'} = "
  echo 'cd public_html/debian ;
  apt-ftparchive generate -c=aptftp.conf aptgenerate.conf;
  apt-ftparchive release -c=aptftp.conf dists/unstable >dists/unstable/Release ;
  rm -f dists/unstable/Release.gpg ;
  gpg -u 3A3CB5A6 -bao dists/unstable/Release.gpg dists/unstable/Release'|
  ssh foo@www.example.com  2>/dev/null ;
  echo 'Package archive created!'";
The postupload hook script initiated by dupload(1) creates updated archive files for each upload.

You can add this small public archive to the apt-line of your client system by the following.

$ sudo bash
# echo "deb http://www.example.com/~foo/debian/ unstable main" \
   >> /etc/apt/sources.list
# apt-key add foo.public.key
        Tip
If the archive is located on the local filesystem, you can use "deb file:///home/foo/debian/ …" instead.


'''

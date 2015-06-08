"""
:Description:
    Python representation of dpkg-scanpackages program for the generation of
    package lists for the repository. This should be called on every add or
    remove so the user doesn't have to be bothered with dpkg-scanpackages calls.
    
:Copyright:
    Angry Coders (C) 2015
    Daniel Kettle
    daniel.kettle@angrycoders.com, initial.dann@gmail.com
   
   
"""

from subprocess import PIPE, Popen
import os

def Packages_gz(webroot, path):
    os.chdir(webroot)
    relpath = os.path.relpath(path)
    # dpkg-scanpackages [repo w/o directory + toplevel] [/dev/null] > [repo w/o directory + toplevel]/Packages.gz
    cmd = "dpkg-scanpackages {} /dev/null | gzip -9c > {}/Packages.gz".format(
        relpath, relpath)
    print(cmd)
    proc = Popen(cmd, shell=True)
    proc.communicate()
    cmd = "dpkg-scanpackages {} /dev/null > {}/Packages".format(
        relpath, relpath)
    print(cmd)
    proc = Popen(cmd, shell=True)
    proc.communicate()
    return proc.returncode


"""
:Description:
    Module for building the debian packages
    Currently relies on the dpkg-deb --build command.
"""

from subprocess import Popen, PIPE

def build_package(path, target="."):
    """
    TODO:
        - Copy package into a temporary directory where it can be built either in a 
          chroot or another folder and have bad hidden files/folders removed
          (.svn, .apt-pkg) before being built
        
    :Parameters:
        - target: Either a directory or a filename;
                  If directory: saves package based on control file data (name_ver_arch.deb)
                  If filename: save package file to filename
    """
    proc = Popen(['dpkg-deb', '--build', path, target])
    proc.communicate()
    return proc.returncode
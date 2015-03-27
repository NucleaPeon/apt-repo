"""
:Description:
    Module for building the debian packages
    Currently relies on the dpkg-deb --build command.
"""

from subprocess import Popen, PIPE
import tempfile
import shutil
import os

def create_deb_struct(path, pkgname, data={}):
    tmpdir = tempfile.mkdtemp(suffix='tmp', prefix=pkgname, 
                              dir=os.path.join(path, pkgname))
    copypath = os.path.join(path, pkgname, tmpdir)
    shutil.copytree(os.path.join(path, pkgname, 'DEBIAN'), os.path.join(copypath, 'DEBIAN'))
    for src, dst in data.get('files', {}).items():
        os.makedirs(os.path.join(copypath, dst), exist_ok=True)
        shutil.copytree(src, os.path.join(copypath, dst)) if os.path.isdir(src) \
            else shutil.copy2(src, os.path.join(copypath, dst))
        
    return tmpdir
    

def build_package(path, pkgname, data={}):
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
    print("Deploying Files to temporary build dir")
    tmpdir = create_deb_struct(path, pkgname, data)
    proc = Popen(['dpkg-deb', '--build', os.path.join(path, tmpdir), "."])
    proc.communicate()
    shutil.rmtree(tmpdir)
    return proc.returncode
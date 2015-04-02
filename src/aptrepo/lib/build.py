"""
:Description:
    Module for building the debian packages
    Currently relies on the dpkg-deb --build command.
"""

from subprocess import Popen, PIPE
import tempfile
import shutil
import os
import sys
import importlib
from decimal import *
import aptrepo.lib.db
import traceback

REMOVE_FILES_FOLDERS = ['__pycache__', '.svn']

SECTIONS = ["admin", "cli-mono", "comm", "database", "debug", "devel", "doc", "editors", "education", "electronics", 
    "embedded", "fonts", "games", "gnome", "gnu-r", "gnustep", "graphics", "hamradio", "haskell", "httpd", "interpreters", "introspection",
    "java", "kde", "kernel", "libdevel", "libs", "lisp", "localization", "mail", "math", "metapackages", "misc", "net",
    "news", "ocaml", "oldlibs", "otherosfs", "perl", "php", "python", "ruby", "science", "shells", "sound", "tasks",
    "tex", "text", "utils", "vcs", "video", "web", "x11", "xfce", "zope"]

def copytree(src, dst, write_into=True):
    os.makedirs(dst, exist_ok=True)
    common = ''
    newdst = ''
    for root, folders, files in os.walk(src): 
        for d in folders:
            common = os.path.commonprefix([src, os.path.join(root, d)])
            newdst = os.path.join(dst, os.path.join(root, d).replace(common, ''))
            os.makedirs(newdst, exist_ok=True)
            #print("Create Dir {} here: {}".format(os.path.join(root, d), newdst))
            
        for f in files:
            common = os.path.commonprefix([src, os.path.join(root, f)])
            newdst = os.path.join(dst, os.path.join(root, f).replace(common, ''))
            # Need to ensure directories exist leading to this file
            #print("Copy File {} here: {}".format(os.path.join(root, f), newdst))
            shutil.copy2(os.path.join(root, f), newdst)
                

def create_deb_struct(path, pkgname, **kwargs):
    tmpdir = tempfile.mkdtemp(suffix='tmp', prefix=pkgname, 
                              dir=os.path.join(path, pkgname))
    
    copypath = os.path.join(path, pkgname, tmpdir)
    os.makedirs(os.path.join(copypath, 'DEBIAN'), exist_ok=True)
    for src, dst in kwargs.get('files', {}).items():
        # TODO: blacklist file types and folders, use os.walk
        if os.path.isdir(src):
            #print("Copy tree {}, {}".format(src, os.path.join(path, pkgname, tmpdir, dst)))
            copytree(src, os.path.join(path, pkgname, tmpdir, dst))
            
        else:
            dstpath = os.path.join(path, pkgname, tmpdir, *dst.split(os.sep)[:-1])
            os.makedirs(dstpath, exist_ok=True)
            shutil.copy2(src, os.path.join(path, pkgname, tmpdir, dst))
        
    return tmpdir
    

def build_package(path, pkgname, **kwargs):
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
    db = aptrepo.lib.db.read_keys(path, pkgname, *aptrepo.lib.db.keys(path, pkgname))
    db.update(kwargs)
    tmpdir = create_deb_struct(path, pkgname, **db)
    remove_non_deployables(tmpdir, *REMOVE_FILES_FOLDERS)
    write_control_file(tmpdir, pkgname, **db)
    proc = Popen(['dpkg-deb', '--build', os.path.join(path, tmpdir), "."])
    proc.communicate()
    shutil.rmtree(tmpdir)
        
    return proc.returncode

def pkg_installed_size(path, append_bytes=None, ignored_files=['DEBIAN']):
    """
    FIXME: Doesn't calculate size recursively
    :Description:
        Recursive method that aims to compile a total Installed-Size value
        for the resulting control file.
        Performs a quick check to ensure the DEBIAN folder is not included.
    """
    bytecount = 0 if append_bytes is None else append_bytes
    if os.path.exists(path):        
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                if root.split(os.sep)[-1] in ignored_files:
                    continue
                    
                for f in files:
                    bytecount += pkg_installed_size(os.path.join(root, f), bytecount) if \
                        os.path.isdir(f) else os.path.getsize(os.path.join(root, f))
            
        else:
            bytecount += os.path.getsize(path)
    
    return bytecount

def write_control_file(path, pkgname, **kwargs):
    umask = os.umask(0o022)
    # TODO Detect if package has a database file and use those
    # Create control file with any data we have to work with:
    controls = kwargs.get('control', {})
    for k, v in controls.items():
        if os.path.exists(v) and os.path.isfile(v):
            print("\tGenerating {}".format(k))
            shutil.copy2(v, os.path.join(path, "DEBIAN", k))
            os.chmod(os.path.join(path, "DEBIAN", k), 0o775)
    
    # Only write this control file if no other "control" file is specified
    # as a control option
    if controls.get('controls', None) is None:
        with open(os.path.join(path, "DEBIAN", "control"), 'w') as cf:
            cf.write("Package: {}\n".format(pkgname))
            cf.write("Version: {}\n".format(kwargs.get('set_version', 0.1)))
            cf.write("Architecture: {}\n".format(' '.join(kwargs.get('architecture'))))
            cf.write("Section: {}\n".format(kwargs.get('section') if kwargs.get('section') in SECTIONS else "misc"))
            cf.write("Essential: {}\n".format("yes" if kwargs.get('essential') else "no"))
            if kwargs.get('depends'):
                cf.write("Depends: {}\n".format(', '.join(kwargs.get('depends'))))
                
            if kwargs.get('recommends'):
                cf.write("Recommends: {}\n".format(', '.join(kwargs.get('recommends'))))
            
            if kwargs.get('suggests'):
                cf.write("Suggests: {}\n".format(', '.join(kwargs.get('suggests'))))
            
            cf.write("Provides: {}\n".format(', '.join(kwargs.get('provides', [pkgname]))))
            size = Decimal(pkg_installed_size(path) / 1024).quantize(Decimal('1.'), rounding=ROUND_UP)
            cf.write("Installed-Size: {}\n".format(size))
            if not kwargs.get('homepage') is None:
                cf.write("Homepage: {}\n".format(kwargs.get('homepage')))
            cf.write("Package-Type: deb\n")
            if not kwargs.get('maintainer') is None:
                cf.write("Maintainer: {}\n".format(', '.join(kwargs.get('maintainer'))))
                
            cf.write("Description: {}\n".format(kwargs.get('desc', 'Description Not Set')))
            for d in kwargs.get('description', ['...']):
                cf.write(" {}\n".format(d))

def remove_non_deployables(toplevel, *non_deployables):
    """
    Non Deployables are files and folders that no one wants deployed on the
    target system. Examples of these are "__pycache__" folders from python,
    ".svn" folders from subversion and other temp files that litter 
    code folders that shouldn't be placed on the target system.
    """
    for root, folders, files in os.walk(toplevel):
        for f in files: 
            if f in non_deployables:
                os.remove(os.path.join(root, f))
                
        for d in folders:
            if d in non_deployables:
                shutil.rmtree(os.path.join(root, d))
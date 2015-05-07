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
import logging

REMOVE_FILES_FOLDERS = ['__pycache__', '.svn']

SECTIONS = ["admin", "cli-mono", "comm", "database", "debug", "devel", "doc", "editors", "education", "electronics", 
    "embedded", "fonts", "games", "gnome", "gnu-r", "gnustep", "graphics", "hamradio", "haskell", "httpd", "interpreters", "introspection",
    "java", "kde", "kernel", "libdevel", "libs", "lisp", "localization", "mail", "math", "metapackages", "misc", "net",
    "news", "ocaml", "oldlibs", "otherosfs", "perl", "php", "python", "ruby", "science", "shells", "sound", "tasks",
    "tex", "text", "utils", "vcs", "video", "web", "x11", "xfce", "zope"]

def copytree(src, dst, write_into=True):
    logging.debug(__name__)
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
    logging.debug(__name__)
    tmpdir = tempfile.mkdtemp(suffix='tmp', prefix=pkgname, 
                              dir=os.path.join(path, pkgname))
    
    copypath = os.path.join(path, pkgname, tmpdir)
    os.makedirs(os.path.join(copypath, 'DEBIAN'), exist_ok=True)
    for deploykeys in ['Files', 'Override']:
        for src, dst in kwargs.get(deploykeys, {}).items():
            # TODO: blacklist file types and folders, use os.walk
            if os.path.isdir(src):
                #print("Copy tree {}, {}".format(src, os.path.join(path, pkgname, tmpdir, dst)))
                copytree(src, os.path.join(path, pkgname, tmpdir, dst))
                
            else:
                dstpath = os.path.join(path, pkgname, tmpdir, *dst.split(os.sep)[:-1])
                os.makedirs(dstpath, exist_ok=True)
                shutil.copy2(src, os.path.join(path, pkgname, tmpdir, dst))
                
    return tmpdir

def create_ipk_struct(path, pkgname, **kwargs):
    logging.debug(__name__)
    tmpdir = tempfile.mkdtemp(suffix='tmp', prefix=pkgname, 
                              dir=os.path.join(path, pkgname))
    copypath = os.path.join(path, pkgname, tmpdir)
    os.makedirs(os.path.join(copypath, 'CONTROL'), exist_ok=True)
    for deploykeys in ['Files', 'Override']:
        for src, dst in kwargs.get(deploykeys, {}).items():
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
    pkg_profiles = kwargs['Build'].get('profiles', ['deb'])
    retcodes = []
    if 'deb' in pkg_profiles:
        retcodes.append(build_deb_package(path, pkgname, **kwargs))

    if 'ipk' in pkg_profiles:
        retcodes.append(build_ipk_package(path, pkgname, **kwargs))

    return retcodes

def build_ipk_package(path, pkgname, **kwargs):
    logging.debug(__name__)
    tmpdir = create_ipk_struct(path, pkgname, **kwargs)
    remove_non_deployables(tmpdir, *REMOVE_FILES_FOLDERS)
    write_ipk_control_file(tmpdir, pkgname, **kwargs)
    write_ipk_archives(tmpdir, pkgname, **kwargs)
    
def write_ipk_archives(path, pkgname, **Kwargs):
    logging.debug(__name__)
    try:
        import tarfile
        with tarfile.open(name="control.tar.gz", mode='w:gz') as tf:
            for f in os.listdir(os.path.join(path, 'CONTROL')):
                tf.add(os.path.join(path, 'CONTROL', f), arcname=f)
                
        #with tarfile.open(name="data.tar.gz", mode='w:gz') as tf:
            
        
    except ImportError:
        logging.error("Tarfile module not installed, failed to create archives. Build Failed.")
        sys.stderr.write("Tarfile module not installed, failed to create archives. Build Failed.")

def build_deb_package(path, pkgname, **kwargs):
    logging.debug(__name__)
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
    tmpdir = create_deb_struct(path, pkgname, **kwargs)
    remove_non_deployables(tmpdir, *REMOVE_FILES_FOLDERS)
    write_deb_control_file(tmpdir, pkgname, **kwargs)
    proc = Popen(['dpkg-deb', '--build', os.path.join(path, tmpdir), "."])
    proc.communicate()
    shutil.rmtree(tmpdir)
        
    return proc.returncode

def write_ipk_control_file(path, pkgname, **kwargs):
    logging.debug(__name__)
    umask = os.umask(0o022)
    controls = kwargs.get('Control', {})
    for k, v in controls.items():
        if os.path.exists(v) and os.path.isfile(v):
            print("\tGenerating {}".format(k))
            shutil.copy2(v, os.path.join(path, "CONTROL", k))
            os.chmod(os.path.join(path, "CONTROL", k), 0o775)
            
    # Only write this control file if no other "control" file is specified
    # as a control option
    if controls.get('controls', None) is None:
        with open(os.path.join(path, "CONTROL", "control"), 'w') as cf:
            cf.write("Package: {}\n".format(pkgname.replace("_", "")))
            pkgkw = kwargs.get('Package', {})
            cf.write("Version: {}\n".format(str(pkgkw.get('set_version', "0.1")).replace("_", "")))
            cf.write("Architecture: {}\n".format(', '.join(pkgkw.get('architecture'))))
            if not pkgkw.get('maintainer') is None:
                cf.write("Maintainer: {}\n".format(', '.join(pkgkw.get('maintainer'))))
                
            for lst in ['depends']: #, 'recommends', 'suggests', 'replaces', 'provides']:
                if pkgkw.get(lst):
                    cf.write("{}: {}\n".format(lst.title(), ' '.join(pkgkw.get(lst))))
            
            cf.write("Description: {}\n".format(pkgkw.get('desc', 'Description Not Set')))

def write_deb_control_file(path, pkgname, **kwargs):
    logging.debug(__name__)
    umask = os.umask(0o022)
    # TODO Detect if package has a database file and use those
    # Create control file with any data we have to work with:
    controls = kwargs.get('Control', {})
    for k, v in controls.items():
        if os.path.exists(v) and os.path.isfile(v):
            print("\tGenerating {}".format(k))
            shutil.copy2(v, os.path.join(path, "DEBIAN", k))
            os.chmod(os.path.join(path, "DEBIAN", k), 0o775)
    
    # Only write this control file if no other "control" file is specified
    # as a control option
    if controls.get('controls', None) is None:
        with open(os.path.join(path, "DEBIAN", "control"), 'w') as cf:
            cf.write("Package: {}\n".format(pkgname.replace("_", "")))
            pkgkw = kwargs.get('Package', {})
            cf.write("Version: {}\n".format(str(pkgkw.get('set_version', "0.1")).replace("_", "")))
            cf.write("Architecture: {}\n".format(', '.join(pkgkw.get('architecture'))))
            cf.write("Section: {}\n".format(pkgkw['section'] if pkgkw.get('section') in SECTIONS else "misc"))
            cf.write("Essential: {}\n".format("yes" if pkgkw.get('essential') else "no"))
            
            for lst in ['depends', 'recommends', 'suggests', 'replaces', 'provides']:
                if pkgkw.get(lst):
                    cf.write("{}: {}\n".format(lst.title(), ', '.join(pkgkw.get(lst))))
        
            size = Decimal(pkg_installed_size(path) / 1024).quantize(Decimal('1.'), rounding=ROUND_UP)
            cf.write("Installed-Size: {}\n".format(size))
            pkgkw = kwargs.get('User', {})
            if not pkgkw.get('homepage') is None:
                cf.write("Homepage: {}\n".format(pkgkw.get('homepage')))
            cf.write("Package-Type: deb\n")
            
            if not pkgkw.get('maintainer') is None:
                cf.write("Maintainer: {}\n".format(', '.join(pkgkw.get('maintainer'))))
            
            cf.write("Description: {}\n".format(pkgkw.get('desc', 'Description Not Set')))
            
            for d in pkgkw.get('description', ['...']):
                cf.write(" {}\n".format(d))

def remove_non_deployables(toplevel, *non_deployables):
    logging.debug(__name__)
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

def pkg_installed_size(path, append_bytes=None, ignored_files=['DEBIAN']):
    logging.debug(__name__)
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
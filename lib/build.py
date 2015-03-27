"""
:Description:
    Module for building the debian packages
    Currently relies on the dpkg-deb --build command.
"""

from subprocess import Popen, PIPE
import tempfile
import shutil
import os
import importlib
from decimal import *



SECTIONS = ["admin", "cli-mono", "comm", "database", "debug", "devel", "doc", "editors", "education", "electronics", 
    "embedded", "fonts", "games", "gnome", "gnu-r", "gnustep", "graphics", "hamradio", "haskell", "httpd", "interpreters", "introspection",
    "java", "kde", "kernel", "libdevel", "libs", "lisp", "localization", "mail", "math", "metapackages", "misc", "net",
    "news", "ocaml", "oldlibs", "otherosfs", "perl", "php", "python", "ruby", "science", "shells", "sound", "tasks",
    "tex", "text", "utils", "vcs", "video", "web", "x11", "xfce", "zope"]

def create_deb_struct(path, pkgname, data={}):
    tmpdir = tempfile.mkdtemp(suffix='tmp', prefix=pkgname, 
                              dir=os.path.join(path, pkgname))
    
    copypath = os.path.join(path, pkgname, tmpdir)
    os.makedirs(os.path.join(copypath, 'DEBIAN'), exist_ok=True)
    for src, dst in data.get('files', {}).items():
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(path, pkgname, tmpdir, dst))
            
        else:
            dstpath = os.path.join(path, pkgname, tmpdir, *dst.split(os.sep)[:-1])
            if not os.path.exists(dstpath):
                os.makedirs(dstpath, exist_ok=True)
            shutil.copy2(src, os.path.join(path, pkgname, tmpdir, dst))
        
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
    
    dbmod = importlib.import_module('lib.db')
    db = dbmod.read_package(os.path.join(path, pkgname))
    
    tmpdir = create_deb_struct(path, pkgname, data)
    write_control_file(os.path.join(path, tmpdir), pkgname, **db)
    proc = Popen(['dpkg-deb', '--build', os.path.join(path, tmpdir), "."])
    proc.communicate()
    shutil.rmtree(tmpdir)
    return proc.returncode

def pkg_installed_size(path, append_bytes=None, ignored_files=[".apt-pkg.db"]):
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
                if root.split(os.sep)[-1].upper() == 'DEBIAN':
                    continue
                    
                for f in files:
                    bytecount += pkg_installed_size(f, bytecount) if os.path.isdir(f) else os.path.getsize(f)
            
        else:
            bytecount += os.path.getsize(path)
    
    return bytecount

def apt_repo_pkg(path):
    import lib.db
    return os.path.exists(os.path.join(path, lib.db.APTPKGDB))

def has_deb_structure(path):
    if os.path.exists(path) and os.path.isdir(path):
        for f in os.listdir(path):
            if f.upper() == "DEBIAN":
                testfile = os.path.join(path, f, "control")
                return os.path.isfile(testfile) and os.path.exists(testfile)
            
    return False

def write_control_file(path, pkgname, **kwargs):
    
    umask = os.umask(0o022)
    # TODO Detect if package has a database file and use those
    # Create control file with any data we have to work with:
    with open(os.path.join(path, "DEBIAN", "control"), 'w') as cf:
        cf.write("Package: {}\n".format(pkgname))
        cf.write("Version: {}\n".format(kwargs.get('version', 0.1)))
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
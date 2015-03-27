"""
Package Tool

    - Creates the folder structure
    - Creates the hidden .apt-pkg folder and template files 
        * this is where changelog, version and other temporary data is saved to
    - Includes methods for reading files in .apt-pkg
"""
import os

APTPKG = '.apt_pkg'

def init_package(path, packagename, **kwargs):
    __write_aptpkg(path, packagename)
    inc_version_file(path, packagename, kwargs.get('version', 0))

def __write_aptpkg(path, packagename):
    os.makedirs(os.path.join(path, packagename, APTPKG), exist_ok=True)

def get_version(path, packagename, version=None):
    v = 0
    if version is None:
        vfile = os.path.join(path, packagename, APTPKG, 'version')
        if os.path.exists(vfile):
            with open(vfile, 'r') as vf:
                v = vf.read()
            
    else:
        v = version
            
    return v

def inc_version_file(path, packagename, version=0, by=0.1, prefix='', 
                   suffix='', distro='', distrover='',vcs='', 
                   vcsver='', datever='', override=''):
    '''
    TODO: fancy versioning rules, for now just have an auto incrementing float
    Writes the version file, can handle various version formats:
        - version: package-name_[1.1.3]_arch.deb
        - prefix: package-name[4.2]_version_arch.deb
        - suffix: package-name_version-[1]_arch.deb
        - distro: package-name_version-[0][ubuntu][1]_arch.deb
                  (suffix, distro, distrover)
        - vcs: package-name_version~[gitSTRING]_arch.deb
                                        [datever or vcsver: 20150131]
               package-name_version~gitHASH+distrodistrover
        - datever: package-name_[20150131]_arch.deb
    '''
    v = get_version(path, packagename, version)
    vfile = os.path.join(path, packagename, APTPKG, 'version')        
    try:
        v = round(float(v) + float(by), 4)
        
    except ValueError as vE:
        print(vE)
        v = str(version)
    
    with open(vfile, 'w') as vf:
        vf.write(str(v) if not override else override) # Override version string
        
    return v


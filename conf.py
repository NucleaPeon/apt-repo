import os
PATH                = os.environ['HOME']
COMPONENTS          = ['main', 'non-free', 'contrib']
ARCH                = ['i386', 'amd64', 'armel', 'armhf']

def Distribution():
    if not os.path.exists(os.path.join(os.sep, 'etc', 'os-release')):
        return None
    
    data = open('/etc/os-release', 'r').readlines()
    name = data[1].split('=')[1].strip('\n')
    distro = None
    if name.lower() == "gentoo":
        distro =  data[2].split('=')[1].replace("\"", "").strip('\n').replace('/','_')
    else:
        distro = data[4].split()[1].replace("\"", "")
    if not distro is None:
        distro = [distro]
    return distro

# Has to be compatible with debian-based Operating Systems
# Works for Mint 14

DISTRIBUTION        = Distribution()

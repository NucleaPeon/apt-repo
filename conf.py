import os
PATH                = os.environ['HOME']
COMPONENTS          = ['main', 'non-free', 'contrib']
ARCH                = ['i386', 'amd64', 'armel', 'armhf']

# Has to be compatible with debian-based Operating Systems
# Works for Mint 14
DISTRIBUTION        = open('/etc/os-release', 'r').readlines()[4].split()[1]


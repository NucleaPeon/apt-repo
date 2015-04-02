import platform

ARCH = {"x86_64": "amd64",
        "x86": "i386",
        "armv7l": "armhf",
        "armv6l": "armhf"} # Beaglebone black arch

def get_arch(arch):
    return ARCH.get(arch, arch)

def arch_dir(architecture):
    if architecture != "source":
        return "binary-{}".format(get_arch(architecture))

    return get_arch(architecture)

def arch():
    return get_arch(platform.machine())
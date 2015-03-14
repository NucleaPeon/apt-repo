__all__ = [ARCH, archdir]

ARCH = {"x86_64": "amd64",
        "x86": "i386"}

def archdir(architecture):
    if architecture != "source":
        return "binary-{}".format(arch(architecture))

    return arch(architecture)
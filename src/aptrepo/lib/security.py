from subprocess import PIPE, Popen
import os
import hashlib

def md5sum_file(path, filename):
    f = os.path.join(path, filename)
    if not os.path.exists(f):
        raise Exception("Attempted to generate hash of file {}, file not found".format(f))
    
    md5 = hashlib.md5()
    with open(f, 'r') as openf:
        md5.update(openf.read().encode("utf-8")) # FIXME: Read in at 128 bytes so we don't overload on huge files
    
    filesize = os.path.getsize(f)
    # format and return it
    # FIXME: we may need to buffer and right-align the filesize for readability and standization
    return " {}\t{} {}".format(md5.hexdigest(), filesize, filename) 

def gen_gpg_key():
    proc = Popen(["gpg", "--gen-key", "--batch"])
    proc.communicate()
    return proc.returncode
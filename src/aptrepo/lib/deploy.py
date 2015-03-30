import os
import shutil

def remove_svn_dirs(path):
    for dirpath, dirnames, filenames in os.walk(path):
        for dname in dirnames:
            if dname == ".svn":
                print(os.path.join(dirpath, dname))
                shutil.rmtree(os.path.join(dirpath, dname))
                
                
def write_into(src, dst, overwrite=True, symlinks=False):
    src = os.path.abspath(src)
    toplevel = src.split(os.sep)[-1]
    target = os.path.join(dst, toplevel)
    if not os.path.exists(target):
        shutil.copytree(src, target, symlinks=symlinks)
    
    else:
        subtarget = target # Initialize before reuse
        print("Directory {} exists...".format(subtarget))
        for dirpath, dirnames, filenames in os.walk(src):
            
            for dname in dirnames:
                subtarget = os.path.join(dst, toplevel, dirpath.split(toplevel)[-1].lstrip(os.sep), dname)
                if not os.path.exists(subtarget):
                    shutil.copytree(os.path.join(dirpath, dname), subtarget, symlinks=symlinks)
                
                else:
                    print("Directory {} exists...".format(subtarget))
            
            for fname in filenames:
                subtarget = os.path.join(dst, toplevel, dirpath.split(toplevel)[-1].strip(os.sep), fname)
                if not os.path.exists(subtarget) or overwrite:
                    shutil.copy2(os.path.join(dirpath, f), subtarget, follow_symlinks=symlinks)
                    
                else:
                    print("File {} exists...".format(subtarget))
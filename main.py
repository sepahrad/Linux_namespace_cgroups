import os
import ctypes


libc = ctypes.CDLL("libc.so.6", use_errno=True)
CLONE_NEWNS = 0x00020000
CLONE_NEWUTS = 0x04000000
CLONE_NEWPID = 0x20000000

def unsharens(flags):
    res = libc.unshare(flags)
    
    if res != 0:
        errno = ctypes.get_errno()
        raise OSError(errno, f"unshare failed: {os.strerror(errno)}")

def set_hostname(name):
    res = libc.sethostname(name.encode('utf-8'), len(name))
    
    if res != 0:
        errno = ctypes.get_errno()
        raise OSError(errno, f"sethostname failed: {os.strerror(errno)}")

def run():
    unsharens(CLONE_NEWPID)
    pid = os.fork()

    if pid == 0:
        unsharens(CLONE_NEWNS | CLONE_NEWUTS)
        set_hostname("mycontainer-ss")
        os.system("mount -t proc proc /mnt/d/MyData/Projects/Linux_namespace_cgroups/myroot/proc")
        os.chroot("/mnt/d/MyData/Projects/Linux_namespace_cgroups/myroot")
        os.chdir("/")
        os.execv("/bin/busybox", ["/bin/busybox", "sh"])
    else:
        cid, status = os.waitpid(pid, 0)
        os.system("umount /mnt/d/MyData/Projects/Linux_namespace_cgroups/myroot/proc")
        print(f"Child process {cid} exited with status {status}")

if __name__ == '__main__':
    run()
import os
import ctypes

libc = ctypes.CDLL("libc.so.6", use_errno=True)
CLONE_NEWNS = 0x00020000
CLONE_NEWUTS = 0x04000000
CLONE_NEWPID = 0x20000000
CLONE_NEWCGROUP	= 0x02000000
CLONE_NEWNET = 0x40000000

ROOT_FS ="/mnt/d/MyData/Projects/Linux_namespace_cgroups/myroot"
BASE_DIR = f"{ROOT_FS}/base"
WORK_DIR = f"{ROOT_FS}/work"
UPPER_DIR = f"{ROOT_FS}/upper"

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

def create_mem_group():
    # cgroup v2 unified hierarchy
    base_dir = '/sys/fs/cgroup'
    cd_dir = os.path.join(base_dir, "ss")

    # Check if cgroup v2 is mounted
    if not os.path.exists(base_dir):
        print(f"Error: {base_dir} does not exist. cgroup v2 may not be mounted.")
        return

    # Try to create cgroup directory
    try:
        if not os.path.exists(cd_dir):
            os.makedirs(cd_dir)
    except (PermissionError, OSError) as e:
        print(f"Error creating cgroup directory {cd_dir}: {e}")
        print("Ensure you're running with sudo")
        return
    
    # Add current process to cgroup using cgroup.procs (v2 style)
    procs_file = os.path.join(cd_dir, 'cgroup.procs')
    try:
        with open(procs_file, 'w') as f:
            f.write(str(os.getpid()))
    except PermissionError as e:
        print(f"Error: Cannot write to {procs_file}: {e}")
        print("Ensure you're running with sudo and memory controller is delegated.")
        return
    except FileNotFoundError:
        print(f"Error: {procs_file} not found. Cgroup directory may not have cgroup.procs interface.")
        print("Check: ls -la /sys/fs/cgroup/ss/")
        return

    # Set memory limit using memory.max (v2 style)
    mem_max_file = os.path.join(cd_dir, 'memory.max')
    try:
        with open(mem_max_file, 'w') as f:
            f.write(str(512 * 1024 * 1024))  # 512 MB
    except FileNotFoundError:
        print(f"Warning: {mem_max_file} not found. Memory controller may not be enabled in cgroup v2.")
    except (PermissionError, OSError) as e:
        print(f"Warning: Cannot set memory limit: {e}")

def child_func(stack):
        #os.system(f"mount -t overlay -o lowerdir={BASE_DIR},upperdir={UPPER_DIR},workdir={WORK_DIR} overlay {ROOT_FS}")
        create_mem_group()
        set_hostname("mycontainer-ss")
        os.system(f"mount -t proc proc {ROOT_FS}/proc")
        os.system(f"mount -t sysfs sysfs {ROOT_FS}/sys")
        os.system(f"mount -t tmpfs none {ROOT_FS}/tmp")
        os.chroot(f"{ROOT_FS}")
        os.chdir("/")
        os.execvp("/bin/busybox", ["/bin/busybox", "sh"])

def run():
    child_func_type = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
    child_func_c = child_func_type(child_func)

    stack = ctypes.c_void_p(libc.sbrk(0))

    pid = libc.clone(child_func_c, stack, CLONE_NEWNS | CLONE_NEWPID | CLONE_NEWUTS | CLONE_NEWCGROUP | CLONE_NEWNET | 17)
    _, status = os.waitpid(pid, 0)

    # unsharens(CLONE_NEWPID)
    # pid = os.fork()

    # if pid == 0:
    #     unsharens(CLONE_NEWNS | CLONE_NEWUTS)
    # else:
    #     cid, status = os.waitpid(pid, 0)
    #     os.system("umount /mnt/d/MyData/Projects/Linux_namespace_cgroups/myroot/proc")
    #     print(f"Child process {cid} exited with status {status}")

if __name__ == '__main__':
    run()
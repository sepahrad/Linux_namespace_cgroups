import os

def run():
    pid = os.fork()


    if pid == 0:
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
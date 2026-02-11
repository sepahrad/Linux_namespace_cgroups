import os

def run():
    pid = os.fork()


    if pid == 0:
        os.execv("/bin/bash", ["/bin/bash"])
    else:
        cid, status = os.waitpid(pid, 0)
        print(cid, status)

if __name__ == '__main__':
    run()
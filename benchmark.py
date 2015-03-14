import subprocess
import os
import time


PROCESS = None

def pre_benchmark_mount():
    global PROCESS
    # Drop all caches
    os.system("sync")
    os.system("echo 3 | sudo dd of=/proc/sys/vm/drop_caches")
    # do a mount
    PROCESS = subprocess.Popen(["python", "loopback.py", "/var/lib/gems", "/mnt/party"])
    time.sleep(1)  # hope that it comes up by this point

def main():
    start = time.time()
    do_work()
    end = time.time()
    print end - start

def do_work():
    do_work_n_times()

def do_work_n_times():
    BASE = '/mnt/party/2.1.0/gems'
    for dir in os.listdir(BASE):
        do_work_once()

def do_work_once():
    BASE = '/mnt/party/2.1.0/gems'
    for dir in os.listdir(BASE):
        # Do a stat(), via os.path.exists().
        os.path.exists(os.path.join(BASE, dir) + 'lib/nonexist.rb')

def post_benchmark_unmount():
    os.system("fusermount -u /mnt/party")
    PROCESS.terminate()

if __name__ == '__main__':
    pre_benchmark_mount()
    main()
    post_benchmark_unmount()

#!/usr/bin/env python

from __future__ import with_statement

from errno import EACCES
from os.path import realpath
from sys import argv, exit
from threading import Lock

import os

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

DO_AGGRESSIVE_CACHE=True
GLOBAL_AGGRESSIVE_CACHE={}
GLOBAL_HILARIOUS_ERROR=None


class Loopback(LoggingMixIn, Operations):
    def __init__(self, root):
        self.root = realpath(root)
        self.rwlock = Lock()

    def __call__(self, op, path, *args):
        #print op, path, args
        return super(Loopback, self).__call__(op, self.root + path, *args)

    def access(self, path, mode):
        #print 'yow', path, mode
        if not os.access(path, mode):
            raise FuseOSError(EACCES)

    chmod = os.chmod
    chown = os.chown

    def create(self, path, mode):
        return os.open(path, os.O_WRONLY | os.O_CREAT, mode)

    def flush(self, path, fh):
        return os.fsync(fh)

    def fsync(self, path, datasync, fh):
        return os.fsync(fh)

    def getattr(self, path, fh=None, evil_cache=GLOBAL_AGGRESSIVE_CACHE):
        if DO_AGGRESSIVE_CACHE:
            global GLOBAL_HILARIOUS_ERROR

            # This is what we're doing a lot of. So let's make a list of
            # which files exist at all.

            if not evil_cache:
                import time
                now = time.time()
                for root, dirnames, filenames in os.walk(self.root):
                    for filename in filenames:
                        evil_cache[os.path.join(root, filename)] = True
                    for dirname in dirnames:
                        evil_cache[os.path.join(root, dirname)] = True
                then = time.time()
                print 'filling cache took', then - now
            #import pprint
            #pprint.pprint(evil_cache.keys())

        # We can then do an O(1) lookup into a Python dict to see if
        # the file exists at all.

            # FIXME: path canonicalization??
            if path not in evil_cache:
                if GLOBAL_HILARIOUS_ERROR:
                    raise GLOBAL_HILARIOUS_ERROR
                else:
                    try:
                        os.lstat('/nonexists')  # get the right error
                    except Exception, e:  # steal it
                        GLOBAL_HILARIOUS_ERROR = e
                        raise

        st = os.lstat(path)
        print 'stat', st
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
            'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    getxattr = None

    def link(self, target, source):
        return os.link(source, target)

    listxattr = None
    mkdir = os.mkdir
    mknod = os.mknod
    open = os.open

    def read(self, path, size, offset, fh):
        with self.rwlock:
            os.lseek(fh, offset, 0)
            return os.read(fh, size)

    def readdir(self, path, fh):
        return ['.', '..'] + os.listdir(path)

    readlink = os.readlink

    def release(self, path, fh):
        return os.close(fh)

    def rename(self, old, new):
        return os.rename(old, self.root + new)

    rmdir = os.rmdir

    def statfs(self, path):
        print 'statfs'
        stv = os.statvfs(path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))

    def symlink(self, target, source):
        return os.symlink(source, target)

    def truncate(self, path, length, fh=None):
        with open(path, 'r+') as f:
            f.truncate(length)

    unlink = os.unlink
    utimens = os.utime

    def write(self, path, data, offset, fh):
        with self.rwlock:
            os.lseek(fh, offset, 0)
            return os.write(fh, data)


if __name__ == '__main__':
    if len(argv) != 3:
        print('usage: %s <root> <mountpoint>' % argv[0])
        exit(1)

    fuse = FUSE(Loopback(argv[1]), argv[2], foreground=True)

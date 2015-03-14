#define _GNU_SOURCE 1
#include <sys/stat.h>
#include <errno.h>
#include <stdio.h>
#include <dlfcn.h>
#include <string.h>

static int (*_lstat64)(const int, const char *, struct stat64 *) = NULL;
static int (*_lstat)(const int, const char *, struct stat *) = NULL;

int __lxstat64(int __ver, __const char *__filename, struct stat64 *__stat_buf)
{

  int ret;

  if (!_lstat64)
    _lstat64 = dlsym(RTLD_NEXT, "__lxstat64");

  // do some C string hackery
  char *dot = strrchr(__filename, '.');
  if (dot && !strcmp(dot, ".rb")) {
    printf("Yay\n");
    errno = ENOENT;
    ret = -1;
  } else {
    printf("boo\n");
    ret = _lstat64(__ver, __filename, __stat_buf);
  }

  return ret;
}

int __lxstat(int __ver, __const char *__filename, struct stat *__stat_buf)
{

  int ret;
  printf("%s\n", __filename);

  if (!_lstat)
    _lstat = dlsym(RTLD_NEXT, "__lxstat");

  // do some C string hackery
  char *dot = strrchr(__filename, '.');
  if (dot && !strcmp(dot, ".rb")) {
    printf("simple Yay\n");
    errno = ENOENT;
    ret = -1;
  } else {
    printf("simple boo\n");
    ret = _lstat(__ver, __filename, __stat_buf);
  }

  return ret;
}

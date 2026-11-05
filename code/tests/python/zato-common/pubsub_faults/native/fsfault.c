/*
 * A preloaded library that delays fsync, fdatasync and the pwrite family, and makes a percentage of them fail
 * with EIO or ENOSPC, for files under one path prefix only. The settings are read from the file named
 * by ZATO_FSFAULT_CONTROL, at most once every 100 milliseconds, so a test changes them while the process runs.
 *
 * The control file has lines of the form name=value:
 *   prefix=/tmp/zato-pubsub-test
 *   delay_us=20000
 *   error_percent=10
 *   errno=EIO
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/uio.h>
#include <time.h>
#include <unistd.h>

#define PATH_SIZE 4096
#define LINE_SIZE 4200
#define RELOAD_NS 100000000L

static char control_path[PATH_SIZE];
static char prefix[PATH_SIZE];
static size_t prefix_len = 0;
static long delay_us = 0;
static long error_percent = 0;
static int error_code = EIO;
static long long last_load_ns = 0;
static unsigned long long random_state = 0;
static pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

static int (*real_fsync)(int) = NULL;
static int (*real_fdatasync)(int) = NULL;
static ssize_t (*real_pwrite)(int, const void *, size_t, off_t) = NULL;
static ssize_t (*real_pwrite64)(int, const void *, size_t, off_t) = NULL;
static ssize_t (*real_pwritev)(int, const struct iovec *, int, off_t) = NULL;

static long long now_ns(void) {
    struct timespec value;
    clock_gettime(CLOCK_MONOTONIC, &value);
    return (long long)value.tv_sec * 1000000000LL + value.tv_nsec;
}

static long parse_long(const char *text) {
    long out = 0;
    while (*text >= '0' && *text <= '9') {
        out = out * 10 + (*text - '0');
        text++;
    }
    return out;
}

static void load_control(void) {
    long long now = now_ns();

    if (now - last_load_ns < RELOAD_NS) {
        return;
    }
    last_load_ns = now;

    if (!control_path[0]) {
        const char *path = getenv("ZATO_FSFAULT_CONTROL");
        if (!path) {
            return;
        }
        strncpy(control_path, path, PATH_SIZE - 1);
    }

    FILE *control = fopen(control_path, "r");
    if (!control) {
        delay_us = 0;
        error_percent = 0;
        return;
    }

    long new_delay = 0;
    long new_percent = 0;
    int new_code = EIO;
    char line[LINE_SIZE];

    while (fgets(line, sizeof(line), control)) {
        line[strcspn(line, "\r\n")] = 0;

        if (strncmp(line, "prefix=", 7) == 0) {
            snprintf(prefix, sizeof(prefix), "%.4000s", line + 7);
            prefix_len = strlen(prefix);
        } else if (strncmp(line, "delay_us=", 9) == 0) {
            new_delay = parse_long(line + 9);
        } else if (strncmp(line, "error_percent=", 14) == 0) {
            new_percent = parse_long(line + 14);
        } else if (strcmp(line, "errno=ENOSPC") == 0) {
            new_code = ENOSPC;
        } else if (strcmp(line, "errno=EIO") == 0) {
            new_code = EIO;
        }
    }

    fclose(control);

    delay_us = new_delay;
    error_percent = new_percent;
    error_code = new_code;
}

static int is_target(int fd) {
    char link[64];
    char path[PATH_SIZE];

    if (!prefix_len) {
        return 0;
    }

    snprintf(link, sizeof(link), "/proc/self/fd/%d", fd);
    ssize_t size = readlink(link, path, sizeof(path) - 1);

    if (size < 0) {
        return 0;
    }
    path[size] = 0;

    return strncmp(path, prefix, prefix_len) == 0;
}

static unsigned long long next_random(void) {
    if (!random_state) {
        random_state = (unsigned long long)now_ns() ^ ((unsigned long long)getpid() << 32);
    }
    random_state ^= random_state << 13;
    random_state ^= random_state >> 7;
    random_state ^= random_state << 17;
    return random_state;
}

/* Returns 0 when the call goes ahead, or the errno that it fails with. */
static int apply_fault(int fd) {
    long delay;
    long percent;
    int code;
    int fails = 0;

    pthread_mutex_lock(&lock);
    load_control();
    delay = delay_us;
    percent = error_percent;
    code = error_code;
    if (delay || percent) {
        if (is_target(fd)) {
            if (percent && (long)(next_random() % 100) < percent) {
                fails = 1;
            }
        } else {
            delay = 0;
        }
    }
    pthread_mutex_unlock(&lock);

    if (delay > 0) {
        struct timespec value;
        value.tv_sec = delay / 1000000;
        value.tv_nsec = (delay % 1000000) * 1000;
        nanosleep(&value, NULL);
    }

    return fails ? code : 0;
}

int fsync(int fd) {
    if (!real_fsync) real_fsync = dlsym(RTLD_NEXT, "fsync");
    int code = apply_fault(fd);
    if (code) { errno = code; return -1; }
    return real_fsync(fd);
}

int fdatasync(int fd) {
    if (!real_fdatasync) real_fdatasync = dlsym(RTLD_NEXT, "fdatasync");
    int code = apply_fault(fd);
    if (code) { errno = code; return -1; }
    return real_fdatasync(fd);
}

ssize_t pwrite(int fd, const void *buffer, size_t count, off_t offset) {
    if (!real_pwrite) real_pwrite = dlsym(RTLD_NEXT, "pwrite");
    int code = apply_fault(fd);
    if (code) { errno = code; return -1; }
    return real_pwrite(fd, buffer, count, offset);
}

ssize_t pwrite64(int fd, const void *buffer, size_t count, off_t offset) {
    if (!real_pwrite64) real_pwrite64 = dlsym(RTLD_NEXT, "pwrite64");
    int code = apply_fault(fd);
    if (code) { errno = code; return -1; }
    return real_pwrite64(fd, buffer, count, offset);
}

ssize_t pwritev(int fd, const struct iovec *vectors, int count, off_t offset) {
    if (!real_pwritev) real_pwritev = dlsym(RTLD_NEXT, "pwritev");
    int code = apply_fault(fd);
    if (code) { errno = code; return -1; }
    return real_pwritev(fd, vectors, count, offset);
}

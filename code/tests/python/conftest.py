# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import gc
import importlib.util
import os
import sys
import tempfile
import threading
from collections import Counter

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import generator_, strlist

    nonegen = generator_[None, None, None]
    strlist = strlist
    threadlist = list[threading.Thread]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The modules whose process-wide state owns background threads, each with the function that stops them. The modules
    # are imported by the tests that use them, not by this conftest, which is loaded before the suites that patch gevent
    # before anything else is imported.
    Stop_Functions = (
        ('zato.common.db_env.engine', 'dispose_cached_engines'),
        ('zato.common.util.memory_trim', 'stop_memory_trimmer'),
        ('zato.common.audit_log.search_index_merge', 'stop_search_index_merger'),
        ('zato.common.audit_log.retention_runner', 'stop_retention_runner'),
    )

    # How long a thread that remains after a test may take to end, in seconds, such as a thread of a receiver
    # of the session that answers a delivery in flight when the test ends
    Thread_End_Timeout = 5.0

    # The shared test library, which has the plugin that reports each failure the moment it occurs
    Test_Lib_Dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zato-common', 'lib')
    Failure_Reports_Plugin = 'failure_reports'

    # The marker of the tests that run after every other test of their run
    Soak_Marker = 'soak'

    # The directory on a disk under which the databases of the tests are kept, as zato.common.test.sql_conformance.disk
    # defines it, and the directory in it with the temporary directories of a run
    Env_Disk_Dir = 'Zato_Test_Disk_Dir'
    Default_Disk_Dir = os.path.join('/tmp', 'zato-test')
    Temporary_Dir_Name = 'tmp'

    # The module that tells whether a directory is on a file system held in memory
    Filesystem_Module_Name = 'zato_test_filesystem'
    Filesystem_Module_Path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..',
        'zato-common', 'src', 'zato', 'common', 'db_env', 'filesystem.py')

    # The variable that names the root of the temporary directories of pytest
    Env_Pytest_Temporary_Root = 'PYTEST_DEBUG_TEMPROOT'

    # The variable that names the temporary directory of the processes that the tests start
    Env_Temporary_Dir = 'TMPDIR'

# ################################################################################################################################
# ################################################################################################################################

# The conftest modules of the suites import the shared test library when pytest loads them, which precedes pytest_configure,
# and this conftest is loaded before them.
sys.path.append(ModuleCtx.Test_Lib_Dir)

# Test support
from logging_teardown import silence_logging_teardown # noqa: E402

# The log handlers of every run are flushed at exit, before the final garbage collection of the interpreter,
# which would otherwise take the lock of the logging module after gevent can no longer switch greenlets.
_ = atexit.register(silence_logging_teardown)

# ################################################################################################################################
# ################################################################################################################################

def _stop_process_wide_threads() -> 'None':
    """ Disposes every cached engine of this process, which stops the background WAL checkpointers, and stops
    the memory trimmer that the pub/sub backend starts, the flushers, the retention runner and the merger of the search indexes
    of the audit log, and the worker threads of the thread pool of the gevent hub.
    """
    for module_name, function_name in ModuleCtx.Stop_Functions:
        if module := sys.modules.get(module_name):
            stop = getattr(module, function_name)
            stop()

    # The worker threads of the thread pool of the gevent hub end as well, and the pool starts new ones when it is next used
    if hub_local := sys.modules.get('gevent._hub_local'):
        if hub := hub_local.get_hub_if_exists():
            hub.threadpool.size = 0

    # gevent lists a greenlet that asked for its thread as a thread of its own until the greenlet is collected,
    # and a finished greenlet held in a reference cycle is collected only by a full collection
    _ = gc.collect()

# ################################################################################################################################
# ################################################################################################################################

def _use_disk_temporary_dir(config:'pytest.Config') -> 'None':
    """ Places the temporary directories of the run, those of pytest, of the tempfile module and of the processes
    that the tests start, on a file system that reaches a disk, so that every database a test keeps in one of them
    syncs its commits as a database of a production system does.
    """

    # The module that reads the mount table is loaded from its file, without the packages above it,
    # which import modules that the suites patching gevent must import only after the patch ..
    spec = importlib.util.spec_from_file_location(ModuleCtx.Filesystem_Module_Name, ModuleCtx.Filesystem_Module_Path)
    filesystem = importlib.util.module_from_spec(spec) # type: ignore
    sys.modules[ModuleCtx.Filesystem_Module_Name] = filesystem
    spec.loader.exec_module(filesystem) # type: ignore

    # .. the base directory is the one that the databases of the tests use ..
    base_dir = os.environ.get(ModuleCtx.Env_Disk_Dir)

    if base_dir is None:
        base_dir = ModuleCtx.Default_Disk_Dir

    temporary_dir = os.path.join(base_dir, ModuleCtx.Temporary_Dir_Name)
    os.makedirs(temporary_dir, exist_ok=True)

    # .. a base directory given on the command line is used as it is ..
    if basetemp := config.option.basetemp:
        os.makedirs(basetemp, exist_ok=True)
        directories = [temporary_dir, basetemp]
    else:
        directories = [temporary_dir]

    # .. provided that it is on a disk, as the temporary directory is.
    for directory in directories:
        if filesystem.is_memory_filesystem(directory):
            raise pytest.UsageError(f'Directory `{directory}` is on a file system held in memory')

    os.environ[ModuleCtx.Env_Pytest_Temporary_Root] = temporary_dir
    os.environ[ModuleCtx.Env_Temporary_Dir] = temporary_dir
    tempfile.tempdir = temporary_dir

# ################################################################################################################################

def pytest_configure(config:'pytest.Config') -> 'None':
    """ Loads the plugin that reports each failure the moment it occurs and places the temporary directories on a disk.
    """
    config.pluginmanager.import_plugin(ModuleCtx.Failure_Reports_Plugin)

    _use_disk_temporary_dir(config)

# ################################################################################################################################
# ################################################################################################################################

def pytest_collection_modifyitems(items:'list[pytest.Item]') -> 'None':
    """ Moves the soak tests behind every other test of the run, each group in the order of its collection.
    """
    other_items:'list[pytest.Item]' = []
    soak_items:'list[pytest.Item]' = []

    for item in items:
        if item.get_closest_marker(ModuleCtx.Soak_Marker):
            soak_items.append(item)
        else:
            other_items.append(item)

    items[:] = other_items + soak_items

# ################################################################################################################################
# ################################################################################################################################

def _get_started_threads() -> 'threadlist':
    """ Returns the threads that the threading module started. A dummy thread stands for a greenlet of a process
    that gevent patched, or for a thread that the threading module did not start, and it cannot be joined.
    """
    out = [thread for thread in threading.enumerate() if not isinstance(thread, threading._DummyThread)]
    return out

# ################################################################################################################################

@pytest.fixture(autouse=True)
def no_thread_outlives_its_test() -> 'nonegen':
    """ Fails a test that leaves a thread running in this process. Later tests fork workers from this process,
    and a forked worker inherits in their locked state the locks that such a thread holds at the time of the fork.
    The threads of the engines and of the memory trimmer that the test started are stopped first,
    and a test that needs an engine again receives a new one. Threads are compared by name, so a test that stops
    a thread of its session and starts it again under the same name leaves nothing behind.
    """
    threads_before = Counter(thread.name for thread in _get_started_threads())

    yield

    _stop_process_wide_threads()

    threads_after = Counter(thread.name for thread in _get_started_threads())
    remaining = threads_after - threads_before

    # A thread that ends shortly after the test is not left behind
    for thread in _get_started_threads():
        if thread.name in remaining:
            thread.join(ModuleCtx.Thread_End_Timeout)

    threads_after = Counter(thread.name for thread in _get_started_threads())

    remaining_names:'strlist' = sorted((threads_after - threads_before).elements())

    assert remaining_names == []

# ################################################################################################################################
# ################################################################################################################################

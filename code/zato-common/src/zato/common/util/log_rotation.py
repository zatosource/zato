# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The log files of a server with several worker processes. Every process appends to each file, and only the arbiter
# renames a file that reached its size limit, after which it reopens its own handlers and asks every worker
# to reopen its handlers. The arbiter renames a file again only after every worker it asked has acknowledged,
# because a worker that has not reopened still appends to the renamed file. The pub/sub writer process, which receives
# no commands, compares its file with the file under its name and writes each record under a shared lock of the directory,
# and the arbiter renames a file only while it holds that lock exclusively.

# stdlib
import fcntl
import logging
import os
from logging.handlers import RotatingFileHandler

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, callable_, list_, set_

    anydict = anydict
    callable_ = callable_

    workerhandlerlist = list_['WorkerFileHandler']
    intset            = set_[int]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The handler class of the logging configuration of a server with one process, and the class that replaces it
    Rotating_Handler_Class = 'logging.handlers.RotatingFileHandler'
    Worker_Handler_Class   = 'zato.common.util.log_rotation.WorkerFileHandler'

# ################################################################################################################################
# ################################################################################################################################

def _open_directory(file_name:'str') -> 'int':
    """ Opens the directory of a log file, whose lock orders the renames of the arbiter and the records
    of a process that follows the renames by itself.
    """
    dir_name = os.path.dirname(file_name)
    out = os.open(dir_name, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    return out

# ################################################################################################################################
# ################################################################################################################################

class WorkerFileHandler(RotatingFileHandler):
    """ A file handler that appends to its file and never renames it. The arbiter renames the file
    and the handler then opens the file under its name again.
    """

    # A handler of a process without a control channel compares its file with the file under its name before each record,
    # under a lock of the directory that it takes through a descriptor of its own
    is_watched = False
    watch_fd:'int'

    def shouldRollover(self, record:'logging.LogRecord') -> 'int':
        """ Leaves the file in place, because the other processes of the server append to it as well.
        """
        return 0

# ################################################################################################################################

    def emit(self, record:'logging.LogRecord') -> 'None':
        if self.is_watched:
            self._emit_watched(record)
        else:
            super().emit(record)

# ################################################################################################################################

    def _emit_watched(self, record:'logging.LogRecord') -> 'None':
        """ Compares the stream with the file under its name and writes the record under a shared lock of the directory
        of the file, which the arbiter takes exclusively to rename the file, so no rename falls between the two.
        """
        fcntl.flock(self.watch_fd, fcntl.LOCK_SH)

        try:
            self._reopen_if_renamed()
            super().emit(record)

        finally:
            fcntl.flock(self.watch_fd, fcntl.LOCK_UN)

# ################################################################################################################################

    def watch(self) -> 'None':
        """ Makes the handler follow the renames of the arbiter by itself. The directory is opened in this process,
        because a lock taken through a descriptor inherited from the arbiter would be the lock of the arbiter.
        """
        self.watch_fd = _open_directory(self.baseFilename)
        self.is_watched = True

# ################################################################################################################################

    def _reopen_if_renamed(self) -> 'None':
        """ Opens the file under its name again when the file of the stream is no longer the one under the name.
        """
        self.acquire()

        try:
            stream_stat = os.fstat(self.stream.fileno())

            # The arbiter may have renamed the file and not yet created the next one ..
            try:
                name_stat = os.stat(self.baseFilename)
            except FileNotFoundError:
                is_renamed = True

            # .. or created the next one already.
            else:
                is_renamed = (name_stat.st_dev, name_stat.st_ino) != (stream_stat.st_dev, stream_stat.st_ino)

            if is_renamed:
                self.stream.close()
                self.stream = self._open()

        finally:
            self.release()

# ################################################################################################################################

    def reopen(self) -> 'None':
        """ Closes the stream of the renamed file and opens the file under its name, under the lock of the handler,
        so that no record is split across two files.
        """
        self.acquire()

        try:
            self.stream.close()
            self.stream = self._open()

        finally:
            self.release()

# ################################################################################################################################

    def rotate_if_due(self) -> 'bool':
        """ Renames the file and its backups when the file reached its size limit, and opens the file under its name again,
        under the lock of the handler. Returns whether the file was renamed.
        """
        # A handler without a limit or without backups keeps one file, as RotatingFileHandler does ..
        if self.maxBytes <= 0:
            return False

        if self.backupCount <= 0:
            return False

        self.acquire()

        try:
            # .. while any other file is renamed once it reaches its limit.
            size = os.stat(self.baseFilename).st_size
            out = size >= self.maxBytes

            if out:
                out = self._rename_unless_written()

        finally:
            self.release()

        return out

# ################################################################################################################################

    def _rename_unless_written(self) -> 'bool':
        """ Renames the file unless a process that follows the renames by itself is writing a record,
        in which case the check of the next interval renames it. Returns whether the file was renamed.
        """
        dir_fd = _open_directory(self.baseFilename)

        try:
            try:
                fcntl.flock(dir_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                out = False
            else:
                self.doRollover()
                out = True

        finally:
            os.close(dir_fd)

        return out

# ################################################################################################################################
# ################################################################################################################################

def get_worker_handlers() -> 'workerhandlerlist':
    """ Returns the worker file handlers of the loggers of this process, one for each file.
    """
    loggers = [logging.getLogger()]

    for item in logging.Logger.manager.loggerDict.values():
        if isinstance(item, logging.Logger):
            loggers.append(item)

    out:'workerhandlerlist' = []
    file_names:'set_[str]' = set()

    for item in loggers:
        for handler in item.handlers:
            if isinstance(handler, WorkerFileHandler):
                if handler.baseFilename not in file_names:
                    file_names.add(handler.baseFilename)
                    out.append(handler)

    return out

# ################################################################################################################################

def reopen_worker_handlers() -> 'None':
    """ Opens each log file of this process under its name again, which a worker does on the command of the arbiter.
    """
    for handler in get_worker_handlers():
        handler.reopen()

# ################################################################################################################################

def watch_worker_handlers() -> 'None':
    """ Makes each log file handler of this process follow the renames of the arbiter by itself,
    which the pub/sub writer process does, because it receives no control commands.
    """
    for handler in get_worker_handlers():
        handler.watch()

# ################################################################################################################################

def use_worker_handlers(config:'anydict') -> 'None':
    """ Replaces the class of each rotating file handler of a logging configuration, before the arbiter applies it.
    """
    for handler_config in config['handlers'].values():
        if handler_config['class'] == ModuleCtx.Rotating_Handler_Class:
            handler_config['class'] = ModuleCtx.Worker_Handler_Class

# ################################################################################################################################
# ################################################################################################################################

class LogRotator:
    """ Renames in the arbiter the log files that reached their size limits and asks every worker to reopen them.
    """

    def __init__(self, handlers:'workerhandlerlist', broadcast_reopen:'callable_') -> 'None':

        # broadcast_reopen receives the ID of a rotation and returns the slots whose workers it asked to reopen their files
        self.handlers = handlers
        self.broadcast_reopen = broadcast_reopen

        self.rotation_id = 0
        self.pending_slots:'intset' = set()

# ################################################################################################################################

    def rotate_due(self) -> 'bool':
        """ Renames each file that reached its limit, unless a worker has not acknowledged the previous rotation,
        and returns whether any file was renamed.
        """
        # A worker that has not reopened its files still appends to the renamed ones, which a rotation now would rename again ..
        if self.pending_slots:
            return False

        # .. each handler of the arbiter renames its file and opens it again ..
        out = False

        for handler in self.handlers:
            if handler.rotate_if_due():
                logger.info('Rotated log file `%s`', handler.baseFilename)
                out = True

        # .. and every worker opens the renamed files again, which it acknowledges with the ID of this rotation.
        if out:
            self.rotation_id += 1
            self.pending_slots = self.broadcast_reopen(self.rotation_id)

        return out

# ################################################################################################################################

    def on_reopened(self, slot:'int', rotation_id:'int') -> 'None':
        """ Records that the worker of a slot reopened its files after a rotation.
        """
        # An acknowledgement of an earlier rotation follows one that the slot sent already
        if rotation_id == self.rotation_id:
            self.pending_slots.discard(slot)

# ################################################################################################################################

    def on_worker_exit(self, slot:'int') -> 'None':
        """ Records that the worker of a slot terminated, so it appends to no file, and its replacement is forked
        with the handlers of the arbiter, which name the current files.
        """
        self.pending_slots.discard(slot)

# ################################################################################################################################
# ################################################################################################################################

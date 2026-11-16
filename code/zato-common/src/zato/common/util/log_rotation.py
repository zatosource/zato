# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The log files of a server that an arbiter started. The arbiter, the worker and the config process append to each file,
# and only the arbiter renames a file that reached its size limit, after which it reopens its own handlers and asks
# the worker and the config process to reopen theirs. The arbiter renames a file again only after each process it asked
# has acknowledged, because a process that has not reopened still appends to the renamed file.

# stdlib
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

class WorkerFileHandler(RotatingFileHandler):
    """ A file handler that appends to its file and never renames it. The arbiter renames the file
    and the handler then opens the file under its name again.
    """

    def shouldRollover(self, record:'logging.LogRecord') -> 'int':
        """ Leaves the file in place, because the other processes of the server append to it as well.
        """
        return 0

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
                self.doRollover()

        finally:
            self.release()

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
    """ Opens each log file of this process under its name again, which a process does on the command of the arbiter.
    """
    for handler in get_worker_handlers():
        handler.reopen()

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
    """ Renames in the arbiter the log files that reached their size limits and asks the worker and the config process
    to reopen them.
    """

    def __init__(self, handlers:'workerhandlerlist', broadcast_reopen:'callable_') -> 'None':

        # broadcast_reopen receives the ID of a rotation and returns the slots whose processes it asked to reopen their files
        self.handlers = handlers
        self.broadcast_reopen = broadcast_reopen

        self.rotation_id = 0
        self.pending_slots:'intset' = set()

# ################################################################################################################################

    def rotate_due(self) -> 'bool':
        """ Renames each file that reached its limit, unless a process has not acknowledged the previous rotation,
        and returns whether any file was renamed.
        """
        # A process that has not reopened its files still appends to the renamed ones, which a rotation now would rename again ..
        if self.pending_slots:
            return False

        # .. each handler of the arbiter renames its file and opens it again ..
        out = False

        for handler in self.handlers:
            if handler.rotate_if_due():
                logger.info('Rotated log file `%s`', handler.baseFilename)
                out = True

        # .. and each process opens the renamed files again, which it acknowledges with the ID of this rotation.
        if out:
            self.rotation_id += 1
            self.pending_slots = self.broadcast_reopen(self.rotation_id)

        return out

# ################################################################################################################################

    def on_reopened(self, slot:'int', rotation_id:'int') -> 'None':
        """ Records that the process of a slot reopened its files after a rotation.
        """
        # An acknowledgement of an earlier rotation follows one that the slot sent already
        if rotation_id == self.rotation_id:
            self.pending_slots.discard(slot)

# ################################################################################################################################

    def on_process_exit(self, slot:'int') -> 'None':
        """ Records that the process of a slot terminated, so it appends to no file, and its replacement is forked
        with the handlers of the arbiter, which name the current files.
        """
        self.pending_slots.discard(slot)

# ################################################################################################################################
# ################################################################################################################################

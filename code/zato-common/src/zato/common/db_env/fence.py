# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The fence of the Zato database on PostgreSQL. The engine factory attaches it to each PostgreSQL engine of the Zato
# database when the engine is built, and each transaction of such an engine first confirms the generation and the owner
# of the server it runs for. The generation guard of a server is bound to the engine that the server took over through
# and to the generation file of the server, so an engine that the same server builds later, e.g. after its engine was
# disposed, confirms the same generation. A process that does not take the database over itself, such as the Dashboard,
# the cleanup process or the enmasse importer, follows the generation that the server of its environment recorded.

# stdlib
import os
from logging import getLogger
from typing import NamedTuple
from weakref import WeakKeyDictionary

# SQLAlchemy
from sqlalchemy import event

# Zato
from zato.common.db_env.common import get_env_value
from zato.common.db_env.pg8000_common import check_rows
from zato.common.db_env.write_path import get_write_path, Mechanism
from zato.common.defaults import default_env_base_dir
from zato.common.pubsub.sql.replaced import raise_replaced

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from zato.common.typing_ import any_, intnone

    # Dummy assignments to satisfy type checkers
    any_ = any_
    intnone = intnone
    Connection = Connection
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The environment variable with the path to the file in which the active server records its generation.
    Env_Generation_File = 'Zato_Database_Generation_File'

    # The names under which the same variable is read, in this order, when it is not set.
    Env_Generation_File_Aliases = ('Zato_PubSub_Generation_File',)

# ################################################################################################################################
# ################################################################################################################################

# The name of the file in which the active server records its generation, under the environment directory.
_generation_file_name = 'database-generation'

# The lines of the generation file - the generation, then the owner.
_generation_file_line_count = 2

# The keys under which a pooled connection records how far its current transaction confirmed the generation.
_state_key = 'zato_pubsub_generation_state'
_state_checked = 'checked'
_state_locked = 'locked'

# The statements that a read begins with - everything else writes, as does a read that locks the rows it selects.
_read_prefix = 'SELECT'
_locking_clauses = (' FOR UPDATE', ' FOR NO KEY UPDATE', ' FOR SHARE', ' FOR KEY SHARE')

# What a transaction runs before its first read and before its first write.
_check_query = 'SELECT 1 FROM zato_active WHERE id = 1 AND generation = %s AND owner = %s'
_lock_query = 'SELECT 1 FROM zato_active WHERE id = 1 AND generation = %s AND owner = %s FOR SHARE'

# ################################################################################################################################
# ################################################################################################################################

class ActiveServer(NamedTuple):
    """ The generation of the active server and the value unique to that server, as the generation file records them.
    """
    generation: int
    owner: str

# ################################################################################################################################
# ################################################################################################################################

def get_generation_file_path() -> 'str':
    """ Returns the path to the file in which the active server records its generation.
    """
    if not (out := get_env_value(ModuleCtx.Env_Generation_File, ModuleCtx.Env_Generation_File_Aliases)):
        msg = f'Environment variable {ModuleCtx.Env_Generation_File} is not set - the default location ' + \
            f'of the generation file under {default_env_base_dir} is no longer supported'
        raise Exception(msg)

    return out

# ################################################################################################################################

def set_environment_generation_file(component_dir:'str') -> 'None':
    """ Points the generation file to the environment directory that contains the directory of a component,
    unless the path is already set in the environment.
    """
    if not get_env_value(ModuleCtx.Env_Generation_File, ModuleCtx.Env_Generation_File_Aliases):
        env_dir = os.path.dirname(os.path.abspath(component_dir))
        os.environ[ModuleCtx.Env_Generation_File] = os.path.join(env_dir, _generation_file_name)

# ################################################################################################################################

def write_generation_file(generation:'int', owner:'str') -> 'None':
    """ Records the generation and the owner of this server for the other processes of the server's environment.
    """
    path = get_generation_file_path()
    temp_path = f'{path}.tmp'

    with open(temp_path, 'w') as generation_file:
        _ = generation_file.write(f'{generation}\n{owner}')

    os.replace(temp_path, path)

# ################################################################################################################################

def _read_generation_file(path:'str') -> 'ActiveServer':
    """ Returns the generation and the owner that a generation file records.
    """
    with open(path) as generation_file:
        value = generation_file.read()

    generation, owner = value.split('\n', _generation_file_line_count - 1)
    generation = int(generation)

    out = ActiveServer(generation, owner)
    return out

# ################################################################################################################################

def read_generation_file() -> 'ActiveServer':
    """ Returns the generation and the owner that the server of this environment recorded.
    """
    path = get_generation_file_path()

    out = _read_generation_file(path)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _is_write(statement:'str') -> 'bool':
    """ Whether a statement changes rows or locks them.
    """
    stripped = statement.lstrip()
    prefix = stripped[:len(_read_prefix)]

    if prefix.upper() != _read_prefix:
        out = True

    else:
        out = False

        for clause in _locking_clauses:
            if clause in statement:
                out = True
                break

    return out

# ################################################################################################################################
# ################################################################################################################################

class _Fences:
    """ The generation guards of this process.
    """

    # The guard of each engine that a server took the database over through
    by_engine:'WeakKeyDictionary[Engine, GenerationGuard]' = WeakKeyDictionary()

    # The guard of each server of this process, by the path of the generation file of the server
    by_generation_file:'dict[str, GenerationGuard]' = {}

    # The guard of each environment that this process follows, by the path of the generation file of the environment
    by_environment:'dict[str, EnvironmentGenerationGuard]' = {}

    # Whether this process follows the generation that the server of its environment recorded
    follows_environment = False

# ################################################################################################################################
# ################################################################################################################################

class GenerationGuard:
    """ Confirms the generation and the owner of a server in each transaction of the engines it is bound to,
    before the first statement of the transaction runs. A read confirms them once, and the first write of a transaction
    also locks the row for share until the transaction ends.
    """

    def __init__(self, generation:'int', owner:'str') -> 'None':
        self.generation = generation
        self.owner = owner

        # Once replaced, a server remains replaced, because generations only ever increase.
        self.is_replaced = False

        # The audit event that the takeover was recorded with, if it was recorded.
        self.takeover_event_id:'intnone' = None

# ################################################################################################################################

    def install(self, engine:'Engine') -> 'None':
        """ Binds the guard to the engine that its server took the database over through and to the generation file
        of its server, so that every engine of the Zato database that the server builds later confirms the same generation.
        """
        generation_file_path = get_generation_file_path()

        _Fences.by_engine[engine] = self
        _Fences.by_generation_file[generation_file_path] = self

# ################################################################################################################################

    def uninstall(self, engine:'Engine') -> 'None':
        """ Releases the guard from an engine and from the generation file of its server.
        """
        if engine in _Fences.by_engine and _Fences.by_engine[engine] is self:
            del _Fences.by_engine[engine]

        for generation_file_path, guard in list(_Fences.by_generation_file.items()):
            if guard is self:
                del _Fences.by_generation_file[generation_file_path]

# ################################################################################################################################

    def _raise_replaced(self) -> 'None':
        message = f'This server was replaced by another one and its pub/sub generation {self.generation} is no longer current'
        raise_replaced(message)

# ################################################################################################################################

    def before_cursor_execute(self, connection:'Connection', cursor:'any_', statement:'str') -> 'None':
        """ Confirms the generation before the first read and before the first write of each transaction.
        """
        if self.is_replaced:
            self._raise_replaced()

        state = connection.info.get(_state_key)

        # The transaction holds the lock already ..
        if state == _state_locked:
            return

        is_write = _is_write(statement)

        # .. or it confirmed the generation and is still only reading ..
        if state == _state_checked and not is_write:
            return

        # .. otherwise, the generation is confirmed now, with the lock for a write.
        if is_write:
            query = _lock_query
            new_state = _state_locked
        else:
            query = _check_query
            new_state = _state_checked

        # Within deferred_replies, the row is confirmed once the reply is read, which precedes the commit.
        cursor.execute(query, (self.generation, self.owner))
        check_rows(connection, cursor, self._confirm_rows)

        connection.info[_state_key] = new_state

# ################################################################################################################################

    def _confirm_rows(self, row_count:'int') -> 'None':
        """ Confirms that the row of the generation and the owner of this server was found.
        """
        if not row_count:
            self.is_replaced = True
            logger.info('Pub/sub generation %s was replaced, this server stops its pub/sub work', self.generation)
            self._raise_replaced()

# ################################################################################################################################
# ################################################################################################################################

class EnvironmentGenerationGuard(GenerationGuard):
    """ Confirms the generation and the owner that the server of an environment recorded in its generation file,
    in a process of the environment that does not take the database over itself. The file is read again whenever
    the server records a new takeover, and with no server of the environment started yet, there is nothing to confirm.
    """

    def __init__(self, generation_file_path:'str') -> 'None':
        super().__init__(0, '')
        self.generation_file_path = generation_file_path

        # Whether a server of the environment recorded its generation
        self.has_server = False

        # The identity and the modification time of the generation file when it was read last
        self._file_version:'tuple[int, int] | None' = None

# ################################################################################################################################

    def _follow_generation_file(self) -> 'None':
        """ Reads the generation file again if the server of the environment recorded a takeover since it was read last.
        """
        if not os.path.exists(self.generation_file_path):
            self.has_server = False
            return

        stat = os.stat(self.generation_file_path)
        file_version = (stat.st_ino, stat.st_mtime_ns)

        # A new takeover of the server of the environment makes its generation current again
        if file_version != self._file_version:
            active_server = _read_generation_file(self.generation_file_path)
            self.generation = active_server.generation
            self.owner = active_server.owner
            self.is_replaced = False
            self._file_version = file_version

        self.has_server = True

# ################################################################################################################################

    def before_cursor_execute(self, connection:'Connection', cursor:'any_', statement:'str') -> 'None':
        """ Confirms the generation that the server of the environment recorded, as of the start of each transaction.
        """
        if _state_key not in connection.info:
            self._follow_generation_file()

        if not self.has_server:
            return

        super().before_cursor_execute(connection, cursor, statement)

# ################################################################################################################################
# ################################################################################################################################

def follow_environment_generation() -> 'None':
    """ Makes every engine of the Zato database of this process confirm the generation that the server
    of its environment recorded, unless a server of this process took the database over itself.
    """
    _Fences.follows_environment = True

# ################################################################################################################################

def _get_environment_guard(generation_file_path:'str') -> 'EnvironmentGenerationGuard':
    """ Returns the guard that follows the generation file of an environment, creating it on first use.
    """
    if generation_file_path not in _Fences.by_environment:
        _Fences.by_environment[generation_file_path] = EnvironmentGenerationGuard(generation_file_path)

    out = _Fences.by_environment[generation_file_path]
    return out

# ################################################################################################################################

def _before_cursor_execute(
    connection:'Connection',
    cursor:'any_',
    statement:'str',
    parameters:'any_',
    context:'any_',
    executemany:'bool',
) -> 'None':
    """ Confirms the generation before the first read and before the first write of each transaction of an engine.
    """

    # The takeover changes the generation that every other transaction confirms ..
    if get_write_path() == Mechanism.Takeover:
        return

    engine = connection.engine

    # .. an engine that a server took the database over through confirms the generation of that server ..
    if engine in _Fences.by_engine:
        _Fences.by_engine[engine].before_cursor_execute(connection, cursor, statement)
        return

    # .. a process with no server that took the database over and that does not follow its environment confirms nothing ..
    if not (_Fences.by_generation_file or _Fences.follows_environment):
        return

    generation_file_path = get_generation_file_path()

    # .. any other engine of a server confirms the generation of the server it is built for ..
    if generation_file_path in _Fences.by_generation_file:
        _Fences.by_generation_file[generation_file_path].before_cursor_execute(connection, cursor, statement)
        return

    # .. an engine of a process that follows its environment confirms the generation of the server of the environment ..
    if _Fences.follows_environment:
        environment_guard = _get_environment_guard(generation_file_path)
        environment_guard.before_cursor_execute(connection, cursor, statement)

    # .. and a server that has not taken the database over yet has no generation to confirm.

# ################################################################################################################################

def _on_transaction_end(connection:'Connection') -> 'None':
    """ A transaction that ended releases its lock, so the next one confirms the generation again.
    """
    # A lost connection is replaced together with its info, and reading the info of the lost one
    # would raise in place of the error that the connection was lost with.
    if connection.invalidated:
        return

    _ = connection.info.pop(_state_key, None)

# ################################################################################################################################

def _on_checkout(dbapi_connection:'any_', connection_record:'any_', connection_proxy:'any_') -> 'None':
    """ A connection taken out of the pool begins with no transaction.
    """
    _ = connection_record.info.pop(_state_key, None)

# ################################################################################################################################

def install_fence(engine:'Engine') -> 'None':
    """ Attaches the fence to every transaction of a PostgreSQL engine of the Zato database.
    """
    event.listen(engine, 'before_cursor_execute', _before_cursor_execute)
    event.listen(engine, 'commit', _on_transaction_end)
    event.listen(engine, 'rollback', _on_transaction_end)
    event.listen(engine, 'checkout', _on_checkout)

# ################################################################################################################################
# ################################################################################################################################

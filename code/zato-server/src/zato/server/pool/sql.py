# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

""" Manages the server's SQL connection pools.
"""

# stdlib
import sys
import copy
import logging
from time import time
from string import Template
from threading import Event
from traceback import format_exc

# SQLAlchemy
from sqlalchemy import pool, create_engine

# Spring Python
from springpython.util import synchronized
from springpython.context import InitializingObject, DisposableObject

# Zato
from zato.common.util import pprint, TRACE1
from zato.common import ZatoException

logger = logging.getLogger(__name__)

def _get_engines(pool_list, crypto_manager, create_sa_engines):
    """ A utility function which builds a dinctionary of engines of a particular
    type, either plain _EngineInfo objects or the actual SQLAlchemy engines.
    """
    engines = {}

    for pool_name in pool_list:
        try:
            password = pool_list[pool_name]["password"]

            # It's possible the pool had been defined but no password
            # has been set yet.
            if password:
                password = str(crypto_manager.decrypt(password))

            engine_params = copy.deepcopy(pool_list[pool_name])
            engine_params["password"] = password

            engine_params_no_password = dict(engine_params.items())
            engine_params_no_password["password"] = "***"

            engine_url = engine_def.substitute(engine_params)

            if create_sa_engines:
                engine = create_engine(engine_url, pool_size=engine_params["pool_size"], **engine_params["extra"])
            else:
                create_engine(engine_url, pool_size=engine_params["pool_size"], **engine_params["extra"])
                engine = _EngineInfo(engine_url, engine_params)

            engines[pool_name] = engine
            logger.debug("SQL connection pool [%s] definition successfully "
                              "read, params=[%s], create_sa_engines=[%s]" % (pool_name,
                                engine_params_no_password, create_sa_engines))

        except Exception, e:
            logger.error(format_exc())

    return engines

class _EngineInfo(object):
    """ A container for informations related to a particular SQL engine.
    """
    def __init__(self, url=None, params=None):
        self.url = url
        self.params = params

class _BaseSQLConnectionPool(InitializingObject):
    """ A base type for classes that deal with SQL connection pools.
    """
    def __init__(self, pool_list, create_sa_engines, crypto_manager):

        # Indicates whether it's safe to check out the connection from a pool.
        # The flag is set when there are any modifications to the pool being
        # performed, such as modyfing the password or changing the pool's size -
        # in that case the calling thread will wait until the pool may be read from.
        self.is_get_allowed = Event()

        # By default it's okay to read from the pool.
        self.is_get_allowed.set()

        # A dictionary describing the paramaters of SQL connection pools
        # available, keyed by names of the pools. Always kept in sync with self.engines.
        self.pool_list = pool_list

        # A dictionary of actual pools, either 'engines' in SQLAlchemy's speak
        # or Zato's _EngineInfo objects. Always kept in sync with self.pool_list.
        self.engines = {}

        # Should that SQL connection pool be used for actually storing the
        # SQL Alchemy engines or merely for storing their configuration.
        self.create_sa_engines = create_sa_engines
        
        self.crypto_manager = crypto_manager

        super(_BaseSQLConnectionPool, self).__init__()

    @synchronized()
    def after_properties_set(self):
        """ Called by Spring Python when the IoC container is starting.
        """

        # Wait until other updates will have been finished (although, in this
        # particular case of 'after_properties_set', there shouldn't be any
        # concurrent updates).
        self.is_get_allowed.wait()

        # Do not allow for any reads or updates during the configuration is being updated.
        self.is_get_allowed.clear()

        try:
            self.engines = _get_engines(self.pool_list, self.crypto_manager, self.create_sa_engines)
        except Exception, e:
            self.logger.error(format_exc())
        finally:
            self.is_get_allowed.set()
            
    def get(self, pool_name, timeout=None):
        """ Returns a connection from the pool of a given name. The calling thread
        will block if the pool manager performs any updates to the underlying
        configuration. The timeout parameter, specified as a float, indicates
        how many seconds to wait before giving up and raising a ZatoException.
        Timeout defaults to None and means the call to .get will block indefinetely.
        Note: in Python < 2.7 the timeout is always ignored and None is used
        instead (that's because it can't be used to tell the reason for
        threading.Event.wait to return, see http://bugs.python.org/issue1674032).
        """
        if timeout and sys.version_info < (2, 7):
            msg = "sys.version_info [%s] is less than 2.7, turning timeout " \
                  "into None, see %s.%s.get documentation for more details" % (sys.version_info,
                    __package__, self.__class__.__name__)
            self.logger.warning(msg)
            timeout = None

        # Wait for any possible updates be finished.
        may_continue = self.is_get_allowed.wait(timeout)

        if sys.version_info >= (2, 7) and timeout and may_continue is not True:
            msg = "Fetching a connection from the pool timed out, " \
                  "sys.version_info=[%s], pool_name=[%s], timeout=[%s], " \
                  "may_continue=[%s]." % (sys.version_info, pool_name,
                    timeout, may_continue)
            self.logger.error(msg)
            raise ZatoException(msg)

        try:
            return self.engines[pool_name]
        except Exception, e:
            msg = "An error has occured while fetching the pool [%s], " \
                  "e=[%s]." % (pool_name, format_exc())
            self.logger.error(msg)
            raise ZatoException(msg)

class ODBConnectionPool(_BaseSQLConnectionPool, DisposableObject):
    pass
        
class SQLConnectionPool(_BaseSQLConnectionPool, DisposableObject):
    """ The actual container for SQLAlchemy's SQL engines, acting as a connection
    pool itself to its clients, each call to .get(pool_name) returns a connection from
    the connection pool managed by SQLAlchemy. The engines are created on IoC
    container startup and disposed of when the IoC container is shutting down.
    It's also possible to create, modify and delete engines while the server
    is running. Updates are synchronized, only one thread at a time will be
    permitted to create, edit or delete an SQL connection pool and during that
    time no other threads will be allowed to neither change connection pools
    nor to fetch the connections.
    """

    # TODO: I don't know where to write it down but here it is.. SQLAlchemy
    # allows one to use connection listeners such as here
    # http://elixir.ematia.de/trac/wiki/FAQ#HowdoIexecuteSQLstatementsatapplicationinitialization
    # and Zato should also support it somehow (for instance, by allowing the user
    # to specify an SQL snippet to execute in the listener).

    def __init__(self, pool_list={}, config_repo_manager=None, crypto_manager=None,
                 create_sa_engines=False, log_name=None):

        _BaseSQLConnectionPool.__init__(self, pool_list, create_sa_engines, crypto_manager)
        super(DisposableObject, self).__init__()

        self.config_repo_manager = config_repo_manager
        self.logger = logging.getLogger("%s.%s[%s]" % (__name__, self.__class__.__name__, log_name))

    @synchronized()
    def _on_config_CREATE_SQL_CONNECTION_POOL(self, params):
        """ Creates a new SQL connection factory.
        """

        # Do not allow for any reads or updates during the pools are being updated.
        self.is_get_allowed.clear()
        try:
            pool_name = params["pool_name"]
            engine = params["engine"]
            user = params["user"]
            host = params["host"]
            db_name = params["db_name"]
            pool_size = int(params["pool_size"])
            extra = params.get("extra", {})

            extra = dict((str(key), extra[key]) for key in extra)

            # The only place where we can check it, while no other updates
            # are allowed.
            pool_exists = self.pool_list.get(pool_name)
            if pool_exists:
                msg = "SQL connection pool [%s] already exists, list_id=[%s]." % (pool_name, id(self.pool_list))
                self.logger.error(msg)
                raise ZatoException(msg)
            else:
                msg = "SQL connection pool [%s] doesn't exist yet, list_id=[%s]." % (pool_name, id(self.pool_list))
                self.logger.log(TRACE1, msg)

            new_pool_list = copy.deepcopy(self.pool_list)
            new_pool_list[pool_name] = {}
            new_pool_list[pool_name]["engine"] = engine
            new_pool_list[pool_name]["user"] = user
            new_pool_list[pool_name]["host"] = host
            new_pool_list[pool_name]["db_name"] = db_name
            new_pool_list[pool_name]["pool_size"] = pool_size
            new_pool_list[pool_name]["extra"] = extra
            new_pool_list[pool_name]["password"] = "" # No password yet.

            engine_url = engine_def.substitute(new_pool_list[pool_name])

            # First save the changes on-disk..
            if not self.create_sa_engines:
                # It's needed here to catch any incorrect extra arguments
                # passed in the URL. It will raise an exception if SingletonServer
                # is trying to create such an incorrect engine definition
                # and the request to create it will never reach the ParallelServers.
                create_engine(engine_url, pool_size=pool_size, **extra)

                self.config_repo_manager.update_sql_pool_list(new_pool_list)

            # .. create the engine ..
            if self.create_sa_engines:
                engine = create_engine(engine_url, pool_size=pool_size, **extra)
            else:
                engine = _EngineInfo(engine_url, params)

            # .. and update the list of pools and engines available.
            self.engines[pool_name] = engine
            self.pool_list = new_pool_list

        except Exception, e:
            msg = "Could not create the SQL connection pool, params=[%s], e=[%s]" % (
                pprint(params), format_exc())
            self.logger.error(msg)
            raise ZatoException(msg)
        finally:
            self.is_get_allowed.set()

    @synchronized()
    def _on_config_EDIT_SQL_CONNECTION_POOL(self, params):
        """ Changes the parameters of an SQL connection pool. Unless only a change
        of the connection name is requested, an old connection pool is disposed
        of and a new one is created.
        """

        # Do not allow for any reads or updates during the pools are being updated.
        self.is_get_allowed.clear()
        try:
            original_pool_name = params["original_pool_name"]
            pool_name = params["pool_name"]
            engine = params["engine"]
            user = params["user"]
            host = params["host"]
            db_name = params["db_name"]
            pool_size = int(params["pool_size"])
            extra = params.get("extra", {})

            extra = dict((str(key), extra[key]) for key in extra)

            old_pool = self.engines[original_pool_name]
            old_params = self.pool_list[original_pool_name]
            old_extra = old_params.get("extra", "")

            new_pool_list = copy.deepcopy(self.pool_list)
            pool_renamed = original_pool_name != pool_name

            # Are we changing the name of a pool only?
            if pool_renamed and (
                engine == old_params["engine"] and user == old_params["user"] and
                host == old_params["host"] and db_name == old_params["db_name"] and
                int(pool_size) == old_params["pool_size"] and extra == old_extra):

                self.logger.debug("Renaming SQL connection pool from [%s] to [%s]" % (original_pool_name, pool_name))

                new_pool_list[pool_name] = new_pool_list.pop(original_pool_name)

                # First save the changes on-disk.
                if not self.create_sa_engines:
                    self.config_repo_manager.update_sql_pool_list(new_pool_list)

                self.engines[pool_name] = self.engines.pop(original_pool_name)
                self.pool_list = new_pool_list

                self.logger.info("SQL connection pool renamed from [%s] to [%s]" % (original_pool_name, pool_name))

            # .. nope, we need to create a new one with updated parameters.
            else:
                self.logger.debug("About to create a new pool with updated parameters.")

                password = old_params["password"]

                if password:
                    password_decrypted = str(self.crypto_manager.decrypt(password))
                else:
                    password_decrypted = ""

                new_params = copy.deepcopy(params)
                new_params["password"] = password_decrypted

                if pool_renamed:
                    new_pool_name = pool_name
                    new_pool_list.pop(original_pool_name)
                    new_pool_list[new_pool_name] = {}
                else:
                    new_pool_name = original_pool_name

                new_pool_list[new_pool_name]["engine"] = engine
                new_pool_list[new_pool_name]["user"] = user
                new_pool_list[new_pool_name]["password"] = password
                new_pool_list[new_pool_name]["host"] = host
                new_pool_list[new_pool_name]["db_name"] = db_name
                new_pool_list[new_pool_name]["pool_size"] = pool_size
                new_pool_list[new_pool_name]["extra"] = extra

                new_engine_url = engine_def.substitute(new_params)

                # First save the changes on-disk.
                if not self.create_sa_engines:
                    # It's needed here to catch any incorrect extra arguments
                    # passed in the URL. It will raise an exception if SingletonServer
                    # is trying to create such an incorrect engine definition
                    # and the request to create it will never reach the ParallelServers.
                    create_engine(new_engine_url, pool_size=pool_size, **extra)

                    self.config_repo_manager.update_sql_pool_list(new_pool_list)

                # .. dispose of the old engine.
                if self.create_sa_engines:
                    self.engines[original_pool_name].dispose()
                    new_engine = create_engine(new_engine_url, pool_size=pool_size, **extra)
                else:
                    new_engine = _EngineInfo(new_engine_url, new_params)

                # .. are the new parameters to be saved under the same pool name?
                if pool_renamed:
                    self.engines.pop(original_pool_name)
                    self.engines[pool_name] = new_engine
                else:
                    self.engines[original_pool_name] = new_engine

                # .. update the list of available pools.
                self.pool_list = new_pool_list

        except Exception, e:
            msg = "Could not update SQL connection pool, params=[%s], e=[%s]" % (pprint(params), format_exc())
            self.logger.error(msg)
            raise ZatoException(msg)
        finally:
            self.is_get_allowed.set()

    @synchronized()
    def _on_config_DELETE_SQL_CONNECTION_POOL(self, params):
        """ Deletes the SQL connection factory.
        """

        # Do not allow for any reads or updates during the pools are being updated.
        self.is_get_allowed.clear()
        try:
            pool_name = params["pool_name"]

            new_pool_list = copy.deepcopy(self.pool_list)
            del new_pool_list[pool_name]

            # First save the changes on-disk..
            if not self.create_sa_engines:
                self.config_repo_manager.update_sql_pool_list(new_pool_list)

            # .. close the pool..
            if self.create_sa_engines:
                self.engines[pool_name].dispose()

            # .. and update the list of pools and engines available.
            del self.engines[pool_name]
            self.pool_list = new_pool_list

        except Exception, e:
            msg = "Could not delete the SQL connection pool, params=[%s], e=[%s]" % (pprint(params), format_exc())
            self.logger.error(msg)
            raise ZatoException(msg)
        finally:
            self.is_get_allowed.set()

    @synchronized()
    def _on_config_CHANGE_PASSWORD_SQL_CONNECTION_POOL(self, params):
        """ Changes the pool's password, which in fact means creating a new pool
        with all the parameters copied from the old one except for the new
        password will be used.
        """
        # Do not allow for any reads or updates while the password's being changed.
        self.is_get_allowed.clear()
        try:
            pool_name = params["pool_name"]
            password = params["password"]
            password_encrypted = params["password_encrypted"]

            new_pool_list = copy.deepcopy(self.pool_list)
            new_params = copy.deepcopy(new_pool_list[pool_name])
            new_params["password"] = password

            new_pool_list[pool_name]["password"] = password_encrypted

            # First save the changes on-disk..
            if not self.create_sa_engines:
                self.config_repo_manager.update_sql_pool_list(new_pool_list)

            new_engine_url = engine_def.substitute(new_params)

            if self.create_sa_engines:
                # .. dispose of the old engine and create a new one..
                self.engines[pool_name].dispose()
                new_engine = create_engine(new_engine_url, pool_size=new_params["pool_size"], **new_params["extra"])
            else:
                new_engine = _EngineInfo(new_engine_url, new_params)

            # .. and assign it to self
            self.engines[pool_name] = new_engine

            # .. update the list of available pools.
            self.pool_list = new_pool_list

        except Exception, e:
            msg = "Could not change the SQL connection pool's password, pool_name=[%s], e=[%s]" % (params["pool_name"], format_exc())
            self.logger.error(msg)
            raise ZatoException(msg)
        finally:
            self.is_get_allowed.set()

    def ping(self, params):
        """ Pings the SQL database and returns the response time, in milliseconds.
        """
        pool_name = params["pool_name"]
        engine = self.engines[pool_name]
        query = ping_queries[self.pool_list[pool_name]["engine"]]

        self.logger.debug("About to ping the SQL connection pool [%s], query=[%s]" % (pool_name, query))

        start_time = time()
        engine.connect().execute(query)
        response_time = time() - start_time

        self.logger.debug("Ping OK, pool_name=[%s], response_time=[%s]" % (pool_name, response_time))

        return response_time

    @synchronized()
    def destroy(self):
        """ Called by Spring Python when the IoC container is shutting down.
        """
        # XXX: That could be a bit smarter..
        if not self.create_sa_engines:
            return

        # Wait until other updates will have been finished.
        self.is_get_allowed.wait()

        # Do not allow for any reads or updates during the pools are being disposed of.
        self.is_get_allowed.clear()

        try:
            if self.engines:
                self.logger.info("Shutting down SQL connection pools.")

                for pool_name, engine in self.engines.items():
                    try:
                        self.logger.debug("Shutting down [%s]." % pool_name)
                        engine.dispose()

                    except Exception, e:
                        self.logger.error(format_exc())
                    else:
                        self.logger.debug("SQL connection pool [%s] shut down." % pool_name)

                self.logger.info("All SQL connection pools shut down successfully.")

            else:
                self.logger.info("No SQL connection pools to shut down.")
                self.is_get_allowed.set()

        except Exception, e:
            self.logger.error(format_exc())
        finally:
            self.is_get_allowed.set()

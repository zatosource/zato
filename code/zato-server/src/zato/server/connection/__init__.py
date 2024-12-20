# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from copy import deepcopy
from traceback import format_exc

# Bunch
from bunch import Bunch, bunchify

# Zato
from zato.common.api import SECRET_SHADOW
from zato.common.dispatch import dispatcher
from zato.common.exception import Inactive
from zato.common.util.api import new_cid

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class BasePoolAPI:
    """ API for pool-based outgoing connections.
    """
    def __init__(self, conn_store):
        self._conn_store = conn_store

    def __getitem__(self, name):
        item = self._conn_store.get(name)
        if not item:
            msg = 'No such connection `{}` in `{}`'.format(name, sorted(self._conn_store.sessions))
            logger.warning(msg)
            raise KeyError(msg)

        if not item.config.is_active:
            msg = 'Connection `{}` is not active'.format(name)
            logger.warning(msg)
            raise Inactive(msg)

        return item

    get = __getitem__

    def create_def(self, name, msg, on_connection_established_callback=None, *args, **kwargs):
        self._conn_store.create(name, msg, on_connection_established_callback, *args, **kwargs)

    create = create_def

    def edit_def(self, name, msg, on_connection_established_callback=None, *args, **kwargs):
        return self._conn_store.edit(name, msg, on_connection_established_callback, *args, **kwargs)

    def delete_def(self, name):
        return self._conn_store.delete(name)

    def change_password_def(self, config):
        return self._conn_store.change_password(config)

# ################################################################################################################################

class BaseConnPoolStore:
    """ Base connection store for pool-based outgoing connections.
    """
    conn_name = None
    dispatcher_events = []
    dispatcher_listen_for = None

    def __init__(self):

        # Import gevent here because connectors may not want to use it
        import gevent
        from gevent.lock import RLock

        self._gevent = gevent
        self._RLock = RLock

        self.sessions = {}
        self.lock = self._RLock()
        self.keep_connecting = set() # IDs of connections to keep connecting for

        # Connects us to interesting events the to-be-established connections need to consult
        dispatcher.listen_for_updates(self.dispatcher_listen_for, self.dispatcher_callback)

        # Maps broker message IDs to their accompanying config
        self.dispatcher_backlog = []

    def __getitem__(self, name):
        return self.sessions[name]

    def get(self, name):
        return self.sessions.get(name)

    def create_session(self, name, config):
        """ Actually adds a new definition, must be called with self.lock held.
        """
        raise NotImplementedError('Must be overridden in subclasses')

    def _log_connection_error(self, name, config_no_sensitive, e, additional=''):
        logger.warning('Could not connect to %s `%s`, config:`%s`, e:`%s`%s', self.conn_name, name, config_no_sensitive,
            format_exc(e), additional)

    def get_config_no_sensitive(self, config):
        config_no_sensitive = deepcopy(config)
        config_no_sensitive['password'] = SECRET_SHADOW

        return config_no_sensitive

    def _create(self, name, config, on_connection_established_callback=None, *args, **kwargs):
        """ Actually establishes a new connection - the method is called in a new greenlet.
        """
        self.keep_connecting.add(config.id)
        session = None
        config_no_sensitive = self.get_config_no_sensitive(config)
        item = Bunch(config=config, config_no_sensitive=config_no_sensitive, is_connected=False, conn=None)

        try:
            logger.debug('Connecting to `%s`', item.config_no_sensitive)

            while item.config.id in self.keep_connecting:

                # It's possible our configuration has been already updated by users
                # even before we first time established any connection. For instance,
                # connection parameters were invalid and the user updated them.
                # We need to learn of the new config or possibly stop connecting
                # at all if we have been deleted.
                with self.lock:
                    keep_connecting, new_config = self.check_dispatcher_backlog(item)

                if keep_connecting:

                    if new_config:
                        item.config = new_config
                        item.config_no_sensitive = self.get_config_no_sensitive(item.config)

                    try:
                        # Will be overridden in a subclass
                        session = self.create_session(name, item.config, item.config_no_sensitive)
                        self.keep_connecting.remove(item.config.id)
                        logger.info('Connected to %s `%r`', self.conn_name, item.config_no_sensitive)

                    except KeyboardInterrupt:
                        return

                    except Exception as e:
                        self._log_connection_error(name, item.config_no_sensitive, e, ', sleeping for 20 s')
                        self._gevent.sleep(20) # TODO: Should be configurable

        except Exception as e:
            self._log_connection_error(name, item.config_no_sensitive, e)
        else:

            # No session, we give up and quit. This may happen if we haveon_dispatcher_events been deleted
            # through a dispatcher event before the session could have been established at all.
            if not session:
                return

            item.conn = session
            item.is_connected = True

            if on_connection_established_callback:
                on_connection_established_callback(item, *args, **kwargs)

        self.sessions[name] = item

        return item

    def create(self, name, config, on_connection_established_callback=None, *args, **kwargs):
        """ Adds a new connection definition.
        """
        with self.lock:
            self._gevent.spawn(self._create, name, config, on_connection_established_callback, *args, **kwargs)

    def delete_session(self, name):
        """ Actually deletes a definition. Must be called with self.lock held.
        """
        item = self.sessions.get(name)
        if item:
            try:
                self.keep_connecting.remove(item.config.id)
            except KeyError:
                pass # It's OK, no ongoing connection attempt at the moment

            self.delete_session_hook(item)

        logger.debug('Could not delete session `%s` - not among `%s`', name, self.sessions)

    def delete_session_hook(self, session):
        """ A hook for concrete subclasses to delete their sessions.
        """
        raise NotImplementedError('Must be overridden in subclasses')

    def delete(self, name):
        """ Deletes an existing connection.
        """
        with self.lock:
            try:
                session = self.sessions.get(name)
                if session and session.is_connected:
                    self.delete_session(name)

            except Exception:
                logger.warning('Error while shutting down session `%s`, e:`%s`', name, format_exc())
            finally:
                self.sessions.pop(name, None)

    def edit(self, name, config, on_connection_established_callback=None, *args, **kwargs):
        with self.lock:
            try:
                self.delete_session(name)
            except Exception:
                logger.warning('Could not delete session `%s`, config:`%s`, e:`%s`', name, config, format_exc())
            else:
                return self._create(config.name, config, on_connection_established_callback, *args, **kwargs)

    def change_password(self, password_data):
        with self.lock:
            new_config = deepcopy(self.sessions[password_data.name].config_no_sensitive)
            new_config.password = password_data.password
            return self.edit(password_data.name, new_config)

# ################################################################################################################################

    def check_dispatcher_backlog(self, item):
        events = []

        for event_info in self.dispatcher_backlog:
            if event_info.ctx.id == item.config.id and event_info.event in self.dispatcher_events:
                events.append(bunchify({
                    'item': item,
                    'event_info': event_info
                }))

        if events:
            return self.on_dispatcher_events(events)
        else:
            return True, None

# ################################################################################################################################

    def dispatcher_callback(self, event, ctx, **opaque):
        self.dispatcher_backlog.append(bunchify({
            'event_id': new_cid(),
            'event': event,
            'ctx': ctx,
            'opaque': opaque
        }))

# ################################################################################################################################

    def on_dispatcher_events(self, events):
        """ Handles in-process dispatcher events. If it's a DELETE, the connection is removed
        from a list of connections to be established. If an EDIT, the connection's config is updated.
        In either case all subsequent dispatcher events are discarded.
        """
        # Only check the latest event
        event = events[-1]
        is_delete = event.event_info.event == self.delete_event

        if is_delete:
            self.keep_connecting.remove(event.item.config.id)
        else:
            new_config = event.event_info.ctx

        # We always delete all the events because we processed the last one anyway
        for event in events:
            self.dispatcher_backlog.remove(event.event_info)

        # Stop connecting if we have just been deleted
        return (False, None) if is_delete else (True, new_config)

# ################################################################################################################################

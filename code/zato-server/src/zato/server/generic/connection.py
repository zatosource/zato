# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Bunch
from bunch import bunchify

# Zato
from zato.common.api import GENERIC
from zato.common.json_internal import dumps, loads
from zato.server.generic import attrs_gen_conn

# ################################################################################################################################

class GenericConnection:
    """ An individual business-level (not SQL one) representation of a generic connection.
    """
    __slots__ = attrs_gen_conn

    def __init__(self):
        self.id = None
        self.name = ''
        self.type_ = ''
        self.is_active = False
        self.is_internal = False
        self.cache_expiry = None
        self.address = None
        self.port = None
        self.timeout = None
        self.data_format = None
        self.opaque = {}
        self.is_channel = False
        self.is_outconn = False

        self.version = None
        self.extra = None
        self.pool_size = None

        self.username = None
        self.username_type = None
        self.secret = ''
        self.secret_type = None

        self.sec_use_rbac = False

        self.conn_def_id = None
        self.cache_id = None
        self.cluster_id = None

# ################################################################################################################################

    @staticmethod
    def from_dict(data, skip=None):
        conn = GenericConnection()
        skip = skip or []
        for key, value in sorted(data.items()):
            if key in skip:
                continue
            try:
                setattr(conn, key, value)
            except AttributeError:
                conn.opaque[key] = value
        return conn

# ################################################################################################################################

    def to_dict(self, needs_bunch=False):
        out = {}
        for name in self.__slots__:
            if name != 'opaque':
                value = getattr(self, name)
                if isinstance(value, bytes):
                    value = value.decode('utf8')
                out[name] = value
        out.update(self.opaque)

        return bunchify(out) if needs_bunch else out

# ################################################################################################################################

    @staticmethod
    def from_model(data):
        instance = GenericConnection()

        opaque_value = getattr(data, GENERIC.ATTR_NAME, None)
        if opaque_value:
            instance.opaque.update(loads(opaque_value))

        for name in instance.__slots__:
            if name != 'opaque':
                value = getattr(data, name, '<no-value-given-{}>'.format(name))
                setattr(instance, name, value)
        return instance

    from_bunch = from_model

# ################################################################################################################################

    def to_sql_dict(self, needs_bunch=False, skip=None):
        out = {}
        skip = skip or []
        for name in self.__slots__:
            if name in skip:
                continue
            if name != 'opaque':
                out[name] = getattr(self, name)
            else:
                out[GENERIC.ATTR_NAME] = dumps(self.opaque)

        return bunchify(out) if needs_bunch else out

# ################################################################################################################################

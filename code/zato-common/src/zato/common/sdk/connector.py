# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Bunch
from zato.common.ext.bunch import Bunch

# Zato
from zato.common.typing_ import dict_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class _FieldBase:
    """ Base class for the schema field types that connectors declare their configuration with.
    """
    def __init__(self, default:'any_'=None) -> 'None':
        self.default = default

# ################################################################################################################################
# ################################################################################################################################

fielddict = dict_[str, _FieldBase]

# ################################################################################################################################
# ################################################################################################################################

class Field:
    """ Schema field types. A connector declares its configuration as class attributes of these types
    and the framework stores, resolves and delivers their values through the connector's self.config.
    """

    class Text(_FieldBase):
        """ A text field.
        """
        def __init__(self, default:'str'='') -> 'None':
            super().__init__(default)

    class Int(_FieldBase):
        """ An integer field.
        """
        def __init__(self, default:'int'=0) -> 'None':
            super().__init__(default)

    class Bool(_FieldBase):
        """ A boolean field.
        """
        def __init__(self, default:'bool'=False) -> 'None':
            super().__init__(default)

    class Secret(_FieldBase):
        """ A field whose value is a secret - it is stored encrypted and it is never returned in listings.
        """
        def __init__(self) -> 'None':
            super().__init__('')

# ################################################################################################################################
# ################################################################################################################################

class Connector:
    """ Base class for user-defined outgoing connection types. A subclass sets the type attribute,
    declares its configuration schema with Field types and implements create_client and ping.
    Invocation methods are plain methods the subclass adds freely - the framework never calls them, services do.
    """

    # The short type name, e.g. 'crm', under which services access connections of this type as self.out.crm.
    type:'str' = ''

    def __init__(self) -> 'None':

        # The name of the connection definition this instance serves.
        self.name = ''

        # The resolved values of the fields the subclass declares.
        self.config = Bunch()

        # The object returned by create_client, set by the framework once the client is built.
        self.client:'any_' = None

        # A logger for the connector to use.
        self.logger = getLogger('zato')

# ################################################################################################################################

    def create_client(self) -> 'any_':
        """ Builds and returns the underlying client object. Called by the framework when the connection starts.
        """
        raise Exception('Method create_client must be implemented by connector subclasses')

# ################################################################################################################################

    def ping(self, client:'any_') -> 'None':
        """ Confirms that the connection is usable, raising an exception if it is not.
        Called by the framework when the connection is pinged.
        """
        raise Exception('Method ping must be implemented by connector subclasses')

# ################################################################################################################################

    def on_stop(self, client:'any_') -> 'None':
        """ Closes the client. Called by the framework when the definition is deleted or edited
        and when the server shuts down. The default implementation does nothing.
        """

# ################################################################################################################################
# ################################################################################################################################

def get_schema(connector_class:'type[Connector]') -> 'fielddict':
    """ Returns all the fields the connector class declares, mapping each field's name to its Field instance.
    """
    out:'fielddict' = {}

    for name in dir(connector_class):
        item = getattr(connector_class, name)
        if isinstance(item, _FieldBase):
            out[name] = item

    return out

# ################################################################################################################################
# ################################################################################################################################

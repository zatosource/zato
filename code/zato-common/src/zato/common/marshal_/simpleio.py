# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.marshal_.api import Model

# ################################################################################################################################
# ################################################################################################################################

if _ := False:
    from dataclasses import Field
    from zato.cy.simpleio import SIOServerConfig
    from zato.server.base.parallel import ParallelServer
    from zato.server.service import Service

    Field = Field
    Service = Service
    SIOServerConfig = SIOServerConfig

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class ModelCtx:
    def __init__(self):
        self.service = None   # type: Service
        self.data = None      # type: dict
        self.DataClass = None # type: object

# ################################################################################################################################
# ################################################################################################################################

class DataClassSimpleIO:

    # We are based on dataclasses, unlike CySimpleIO
    is_dataclass = True

    def __init__(self, server, server_config, user_declaration):
        # type: (ParallelServer, SIOServerConfig, object) -> None
        self.server = server
        self.server_config = server_config
        self.user_declaration = user_declaration

    @staticmethod
    def attach_sio(server, server_config, class_):
        """ Given a service class, the method extracts its user-defined SimpleIO definition
        and attaches the Cython-based one to the class's _sio attribute.
        """
        try:
            # Get the user-defined SimpleIO definition
            user_sio = getattr(class_, 'SimpleIO', None)

            # This class does not use SIO so we can just return immediately
            if not user_sio:
                return

            # Attach the Cython object representing the parsed user definition
            sio = DataClassSimpleIO(server, server_config, user_sio)
            sio.service_class = class_
            class_._sio = sio

        except Exception:
            logger.warn('Could not attach DataClassSimpleIO to class `%s`, e:`%s`', class_, format_exc())
            raise

# ################################################################################################################################

    def parse_input(self, data, _ignored_data_format, service, extra):
        # type: (dict, object, Service, object)

        # If we have a SimpleIO input declared ..
        if getattr(self.user_declaration, 'input', None):

            # .. if it already is a model, we give it to the service as-is ..
            if isinstance(data, Model):
                return data

            # .. otherwise, it must be a dict and we extract its contents.
            return self.server.marshal_api.from_dict(service, data, self.user_declaration.input, extra)

# ################################################################################################################################
# ################################################################################################################################

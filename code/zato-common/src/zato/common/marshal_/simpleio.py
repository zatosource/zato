# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# orjson
from orjson import loads

# Zato
from zato.common import DATA_FORMAT
from zato.common.marshal_.api import Model
from zato.common.pubsub import PubSubMessage

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from dataclasses import Field
    from zato.common.typing_ import any_
    from zato.cy.simpleio import SIOServerConfig
    from zato.server.base.parallel import ParallelServer
    from zato.server.service import Service

    Field = Field
    Service = Service
    ParallelServer = ParallelServer
    SIOServerConfig = SIOServerConfig

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

_dict_like = {DATA_FORMAT.DICT, DATA_FORMAT.JSON}

# ################################################################################################################################
# ################################################################################################################################

class DataClassSimpleIO:

    service_class: 'Service'

    # We are based on dataclasses, unlike CySimpleIO
    is_dataclass = True

    def __init__(
        self,
        server,          # type: ParallelServer
        server_config,   # type: SIOServerConfig
        user_declaration # type: any_
    ) -> 'None':

        self.server = server
        self.server_config = server_config
        self.user_declaration = user_declaration

    @staticmethod
    def attach_sio(server, server_config, class_):
        """ Given a service class, the method extracts its user-defined SimpleIO definition
        and attaches the Cython-based one to the class's _sio attribute.
        """
        try:
            # pylint: disable=attribute-defined-outside-init

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
            logger.warning('Could not attach DataClassSimpleIO to class `%s`, e:`%s`', class_, format_exc())
            raise

# ################################################################################################################################

    def parse_input(
        self,
        data,        # type: any_
        data_format, # type: any_
        service,     # type: Service
        extra        # type: any_
    ) -> 'any_':

        # If we have a SimpleIO input declared ..
        if getattr(self.user_declaration, 'input', None):

            # .. if it already is a model, we give it to the service as-is ..
            if isinstance(data, Model):
                return data

            elif isinstance(data, PubSubMessage):
                data = data.data

            # .. otherwise, it can be a dict and we extract its contents.
            if data_format in _dict_like and (not isinstance(data, (dict))):
                if not isinstance(data, list):
                    data = loads(data)
            return self.server.marshal_api.from_dict(service, data, self.user_declaration.input, extra)

# ################################################################################################################################
# ################################################################################################################################

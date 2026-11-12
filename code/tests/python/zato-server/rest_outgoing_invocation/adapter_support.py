# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the adapter tests build their services with - an adapter instance with the request, the response, the configuration
# and the connection facades that its handle method reads, without the service store of a running server.

# Zato
from zato.common.api import DATA_FORMAT
from zato.common.odata.client import ODataClient
from zato.common.odata.common import ODataVersion
from zato.server.reqresp.response import Response as ServiceResponse

# Test support
from support import Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict
    from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper
    from endpoint import TestEndpoint

# ################################################################################################################################
# ################################################################################################################################

class _RequestStub:
    """ The part of a service's request that adapters read - the raw input and the parsed input.
    """

    def __init__(self, data:'stranydict') -> 'None':
        self.raw = data
        self.input = data

# ################################################################################################################################

class _RESTConnectionItem:
    """ One entry of the REST connections of a service, holding the connection itself.
    """

    def __init__(self, conn:'HTTPSOAPWrapper') -> 'None':
        self.conn = conn

# ################################################################################################################################

class _OutgoingStub:
    """ The outgoing connections of a service, as far as adapters read them.
    """

    def __init__(self) -> 'None':
        self.rest:'dict[str, _RESTConnectionItem]' = {}

# ################################################################################################################################

class _CloudConnectionItem:
    """ One Microsoft cloud connection of a service, holding the client it invokes.
    """

    def __init__(self, connection:'any_') -> 'None':
        self.connection = connection

# ################################################################################################################################

class _MicrosoftStub:
    """ The Microsoft cloud connections of a service.
    """

    def __init__(self) -> 'None':
        self.cloud:'dict[str, _CloudConnectionItem]' = {}

# ################################################################################################################################
# ################################################################################################################################

def new_adapter(
    adapter_class:'any_',
    *,
    data:'stranydict | None'=None,
    rest:'dict[str, HTTPSOAPWrapper] | None'=None,
    cloud:'anydict | None'=None,
    odata:'anydict | None'=None,
    sap:'anydict | None'=None,
    config:'anydict | None'=None,
    ) -> 'any_':
    """ Returns an adapter instance ready for its handle method to run, with the given input and connections.
    """
    if data is None:
        data = {}

    out = adapter_class.__new__(adapter_class)

    out.cid = Test_CID
    out.request = _RequestStub(data)

    out.response = ServiceResponse()
    out.response.init(Test_CID, None, DATA_FORMAT.JSON)

    out.out = _OutgoingStub()
    out.microsoft = _MicrosoftStub()
    out.odata = {}
    out.sap = {}
    out.config = {}

    if rest:
        for name, conn in rest.items():
            out.out.rest[name] = _RESTConnectionItem(conn)

    if cloud:
        for name, connection in cloud.items():
            out.microsoft.cloud[name] = _CloudConnectionItem(connection)

    if odata:
        out.odata = odata

    if sap:
        out.sap = sap

    if config:
        out.config = config

    return out

# ################################################################################################################################

def new_odata_client(endpoint:'TestEndpoint', path:'str') -> 'ODataClient':
    """ Returns an OData 4.0 client of the service under the path, without authentication.
    """
    config = {
        'address': endpoint.http_base + path,
        'odata_version': ODataVersion.V4,
        'auth_type': 'none',
    }

    out = ODataClient(config)
    return out

# ################################################################################################################################
# ################################################################################################################################

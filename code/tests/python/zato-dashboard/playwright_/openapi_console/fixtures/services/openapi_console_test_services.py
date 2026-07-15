# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from json import dumps

# Zato
from zato.common.typing_ import list_, optional
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

# The deterministic values the typed service always replies with - tests assert on them byte by byte.
User_Name  = 'openapi.test.user'
User_ID    = 123
Is_Manager = True
Street     = '25 Integration Street'
City       = 'Testville'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Address(Model):
    street: str
    city:   str

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class GetUserRequest(Model):
    username:      str
    max_results:   int
    needs_details: bool
    locale:        optional[str]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class GetUserResponse(Model):
    user_name:  str
    user_id:    int
    is_manager: bool
    address:    Address
    role_list:  list_[str]

# ################################################################################################################################
# ################################################################################################################################

class TypedGetUser(Service):
    """ A service with typed input and output - its auto channel must be documented as POST
    with the real model schemas and its response is deterministic for try-it assertions.
    """
    name   = 'api.test.openapi.typed.get-user'
    input  = GetUserRequest
    output = GetUserResponse

    def handle(self) -> 'None':

        address = Address()
        address.street = Street
        address.city = City

        out = GetUserResponse()
        out.user_name = User_Name
        out.user_id = User_ID
        out.is_manager = Is_Manager
        out.address = address
        out.role_list = ['integration', 'testing']

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class UntypedEcho(Service):
    """ A service with no typed input or output - its auto channel must be documented
    with the default any-JSON-object schema.
    """
    name = 'api.test.openapi.untyped.echo'

    def handle(self) -> 'None':
        self.response.payload = dumps({'echo': True})
        self.response.content_type = 'application/json'

# ################################################################################################################################
# ################################################################################################################################

class MethodsMulti(Service):
    """ A service with handle_GET and handle_POST - its auto channel must be documented
    with both operations.
    """
    name = 'api.test.openapi.methods.multi'

    def handle_GET(self) -> 'None':
        self.response.payload = dumps({'method': 'GET'})
        self.response.content_type = 'application/json'

    def handle_POST(self) -> 'None':
        self.response.payload = dumps({'method': 'POST'})
        self.response.content_type = 'application/json'

# ################################################################################################################################
# ################################################################################################################################

class PrestartedPing(Service):
    """ The only service matching the active patterns - its auto channel must boot active,
    while every other auto channel boots inactive.
    """
    name = 'api.test.openapi.prestarted.ping'

    def handle(self) -> 'None':
        self.response.payload = dumps({'ping': 'pong'})
        self.response.content_type = 'application/json'

# ################################################################################################################################
# ################################################################################################################################

class ExcludedHidden(Service):
    """ A service matching both an include and an exclude pattern - the exclude wins
    and no auto channel may ever exist for it.
    """
    name = 'api.test.openapi.excluded.hidden'

    def handle(self) -> 'None':
        self.response.payload = dumps({'excluded': True})
        self.response.content_type = 'application/json'

# ################################################################################################################################
# ################################################################################################################################

class NoMatch(Service):
    """ A service matching no include pattern at all - no auto channel may ever exist for it.
    """
    name = 'api.other.no-match'

    def handle(self) -> 'None':
        self.response.payload = dumps({'matched': False})
        self.response.content_type = 'application/json'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ContractResponse(Model):
    contract_id:   int
    customer_name: str
    total_value:   int

# ################################################################################################################################
# ################################################################################################################################

class DiffingContract(Service):
    """ The initial version of the contract-diffing service - a later version with a field
    removed from the output is hot-deployed by the diffing test to trigger a breaking-change report.
    """
    name   = 'api.test.openapi.diffing.contract'
    output = ContractResponse

    def handle(self) -> 'None':

        out = ContractResponse()
        out.contract_id = 456
        out.customer_name = 'Test Customer'
        out.total_value = 10_000

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

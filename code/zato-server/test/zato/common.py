# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import List as list_

# Bunch
from bunch import Bunch

# Zato
from zato.common.ext.dataclasses import dataclass
from zato.server.service import Model, Service

# ################################################################################################################################

sio_config = Bunch()

sio_config.int = Bunch()
sio_config.bool = Bunch()
sio_config.secret = Bunch()
sio_config.bytes_to_str = Bunch()

sio_config.int.prefix = set()
sio_config.int.exact = set()
sio_config.int.suffix = {'_id'}

sio_config.bool.prefix = set()
sio_config.bool.exact = set()
sio_config.bool.suffix = set()

service_name = 'my.service'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class User(Model):
    user_name: str

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Account(Model):
    account_no: int

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class AccountList(Model):
    account_list: list_[Account]

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class MyRequest(Model):
    request_id: int
    user: User

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MyResponse(Model):
    current_balance: int
    last_account_no: int = 567

# ################################################################################################################################
# ################################################################################################################################

class CyMyService(Service):
    """ This is my service.

    It has a docstring.
    """

    invokes = ['abc.def', 'qwe.rty']

    class SimpleIO:
        """
        * input_req_user_id - This is the first line.

        Here is another.

        And here
        are some
        more lines.

        * input_opt_user_name - b111

        * output_req_address_id - c111 c222 c333 c444

        * output_opt_address_name - d111

          d222
        """
        input_required = 'input_req_user_id', 'input_req_customer_id'
        input_optional = 'input_opt_user_name', 'input_opt_customer_name'
        output_required = 'output_req_address_id', 'output_req_address_name'
        output_optional = 'output_opt_address_type', 'output_opt_address_subtype'

# ################################################################################################################################
# ################################################################################################################################

class DataclassMyService(Service):
    """ This is my service.

    It has a docstring.
    """

    invokes = ['abc.def', 'qwe.rty']

    class SimpleIO:
        input  = MyRequest
        output = MyResponse

# ################################################################################################################################
# ################################################################################################################################

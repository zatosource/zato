# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Bunch
from bunch import Bunch

# Zato
from zato.server.service import Service

# ################################################################################################################################

sio_config = Bunch()

sio_config.int = Bunch()
sio_config.bool = Bunch()
sio_config.secret = Bunch()
sio_config.bytes_to_str = Bunch()

sio_config.int.prefix = set()
sio_config.int.exact = set()
sio_config.int.suffix = set(['_id'])

sio_config.bool.prefix = set()
sio_config.bool.exact = set()
sio_config.bool.suffix = set()

service_name = 'my.service'

# ################################################################################################################################
# ################################################################################################################################

class MyService(Service):
    """ This is my service.

    It has a docstring.
    """

    invokes = ['abc.def', 'qwe.rty']

    class SimpleIO:
        """
        * user_id - This is the first line.

        Here is another.

        This
        description
        is split
        into multiple lines.

        * user_name - b111

        * address_id - c111 c222 c333 c444

        * address_name - d111

          d222
        """
        input_required = 'user_id', 'customer_id'
        input_optional = 'user_name', 'customer_name'
        output_required = 'address_id', 'address_name'
        output_optional = 'address_type', 'address_subtype'

# ################################################################################################################################
# ################################################################################################################################

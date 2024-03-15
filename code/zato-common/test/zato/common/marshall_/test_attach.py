# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main

# Zato
from zato.common.ext.dataclasses import dataclass
from zato.common.marshal_.api import Model
from zato.common.marshal_.simpleio import DataClassSimpleIO
from zato.common.test import BaseSIOTestCase
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False, repr=False)
class User(Model):
    user_name: str

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=True, repr=False)
class MyRequest(Model):
    request_id: int
    user: User

# ################################################################################################################################
# ################################################################################################################################

class SIOAttachTestCase(BaseSIOTestCase):

    def test_attach_sio(self):

        class MyService(Service):
            class SimpleIO:
                input = MyRequest

        DataClassSimpleIO.attach_sio(None, self.get_server_config(), MyService)
        self.assertIsInstance(MyService._sio, DataClassSimpleIO)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from .base import MyRequest
from zato.common.marshal_.api import ElementMissing, MarshalAPI
from zato.common.test import rand_int

# ################################################################################################################################
# ################################################################################################################################

class ValidationTestCase(TestCase):

    def test_validate_dict(self):

        request_id   = rand_int()

        # The user element is entirely missing here
        data = {
            'request_id': request_id,
        }

        service = None
        api = MarshalAPI()

        with self.assertRaises(ElementMissing) as e:
            api.from_dict(service, data, MyRequest) # type: MyRequest
            self.assertEquals(e.msg, 'Element missing: /user')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################

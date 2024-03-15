# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from unittest import main

# Zato
from zato.common.test import BaseSIOTestCase
from zato.common.test.apispec_ import CyMyService

# Zato - Cython
from zato.simpleio import CySimpleIO

# ################################################################################################################################
# ################################################################################################################################

class SIOEvalTestCase(BaseSIOTestCase):

    def test_eval_bool(self):

        MyClass = deepcopy(CyMyService)
        CySimpleIO.attach_sio(None, self.get_server_config(), MyClass)
        sio = MyClass._sio # type: CySimpleIO

        elem_name = 'is_abc'
        encrypt_func = None

        value = ''
        result = sio.eval_(elem_name, value, encrypt_func)
        self.assertIsInstance(result, bool)
        self.assertFalse(result)

        value = None
        result = sio.eval_(elem_name, value, encrypt_func)
        self.assertIsInstance(result, bool)
        self.assertFalse(result)

        value = 't'
        result = sio.eval_(elem_name, value, encrypt_func)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

        value = 'true'
        result = sio.eval_(elem_name, value, encrypt_func)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

        value = 'on'
        result = sio.eval_(elem_name, value, encrypt_func)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_eval_int(self):

        MyClass = deepcopy(CyMyService)
        CySimpleIO.attach_sio(None, self.get_server_config(), MyClass)
        sio = MyClass._sio # type: CySimpleIO

        elem_name = 'user_id'
        encrypt_func = None

        value = ''
        result = sio.eval_(elem_name, value, encrypt_func)
        self.assertIsNone(result)

        value = None
        result = sio.eval_(elem_name, value, encrypt_func)
        self.assertIsNone(result)

        value = '111'
        result = sio.eval_(elem_name, value, encrypt_func)
        self.assertIsInstance(result, int)
        self.assertEqual(result, 111)

        value = 222
        result = sio.eval_(elem_name, value, encrypt_func)
        self.assertIsInstance(result, int)
        self.assertEqual(result, 222)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################

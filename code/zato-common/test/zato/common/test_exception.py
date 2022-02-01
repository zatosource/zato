# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from traceback import format_exc
from unittest import main, TestCase

# Zato
from zato.common.util.exception import pretty_format_exception

# ################################################################################################################################
# ################################################################################################################################

class ExceptionTestCase(TestCase):
    def test_pretty_format_exception(self):

        e = None
        abc = 123
        zxc = int, float, dict

        try:
            print(12345 * 1/0)
        except ZeroDivisionError as exc:
            print('********')
            print(format_exc())
            print('********')
            e = exc

        if not e:
            self.fail('Expected for an exception to have been raised')

        result = pretty_format_exception(e)

        print('--------')
        print(result)
        print('--------')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################

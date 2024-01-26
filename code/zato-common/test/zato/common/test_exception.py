# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.util.exception import pretty_format_exception
from zato.common.version import get_version

# ################################################################################################################################
# ################################################################################################################################

class ExceptionTestCase(TestCase):

    maxDiff = 1234567890

    def test_pretty_format_exception(self):

        # Filter our warnings coming from zato --version
        import warnings
        warnings.filterwarnings(action='ignore', message='unclosed file', category=ResourceWarning)

        # Test data
        cid = '123456'
        zato_version = get_version()

        def utcnow_func():
            return '2222-11-22T00:11:22'

        e = None

        try:
            print(12345 * 1/0)
        except ZeroDivisionError as exc:
            e = exc

        if not e:
            self.fail('Expected for an exception to have been raised')

        result = pretty_format_exception(e, cid, utcnow_func)

        expected = f"""
··· Error ···

>>> ZeroDivisionError: 'division by zero'
>>> File "code/zato-common/test/zato/common/test_exception.py", line 39, in test_pretty_format_exception
>>>   print(12345 * 1/0)

··· Details ···

Traceback (most recent call last):
  File "code/zato-common/test/zato/common/test_exception.py", line 39, in test_pretty_format_exception
    print(12345 * 1/0)
ZeroDivisionError: division by zero

··· Context ···

123456
2222-11-22T00:11:22
{zato_version}
        """.strip()

        self.assertEqual(result, expected)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

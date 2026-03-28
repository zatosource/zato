# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys

# local
from test_basic_flow import TestBasicFlow
from test_after_unsubscribe import TestAfterUnsubscribe
from test_permissions import TestPermissions
from test_multi_user import TestMultiUser
from test_auth import TestAuth
from test_consume_once import TestConsumeOnce

# ################################################################################################################################
# ################################################################################################################################

def run_all():
    tests = [
        TestBasicFlow,
        TestAfterUnsubscribe,
        TestPermissions,
        TestMultiUser,
        TestAuth,
        TestConsumeOnce,
    ]

    passed = 0
    failed = 0

    for test_class in tests:
        test = test_class()
        if test.execute():
            passed += 1
        else:
            failed += 1
        print()

    print('=' * 50)
    print(f'Results: {passed} passed, {failed} failed')
    print('=' * 50)

    return failed == 0

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    success = run_all()
    sys.exit(0 if success else 1)

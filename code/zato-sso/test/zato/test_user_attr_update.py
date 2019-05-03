# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from unittest import main

# dateutil
from dateutil.parser import parse as dt_parse

# ipaddress
from ipaddress import ip_address

# Zato
from base import BaseTest, Config, logger
from zato.common.ipaddress_ import ip_network
from zato.sso import const, status_code

# ################################################################################################################################
# ################################################################################################################################

class UserAttrTestCase(BaseTest):

# ################################################################################################################################

    def xtest_update(self):

        name = self._get_random_data()
        value = self._get_random_data()
        expiration = 900

        new_value = self._get_random_data()
        new_expiration = 123

        self.post('/zato/sso/user/attr', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'name': name,
            'value': value,
            'expiration': expiration
        })

        self.patch('/zato/sso/user/attr', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'name': name,
            'value': new_value,
            'expiration': new_expiration
        })

# ################################################################################################################################

    def xtest_update_for_another_user_by_super_user(self):

        username = self._get_random_username()
        password = self._get_random_data()

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username,
            'password': password,
        })

        user_id = response.user_id
        self._approve(user_id)

        name = self._get_random_data()
        value = self._get_random_data()
        expiration = 900

        self.post('/zato/sso/user/attr', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id,
            'name': name,
            'value': value,
            'expiration': expiration
        })

        new_value = self._get_random_data()
        new_expiration = 123

        self.patch('/zato/sso/user/attr', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id,
            'name': name,
            'value': new_value,
            'expiration': new_expiration
        })

# ################################################################################################################################

    def test_update_for_another_user_by_regular_user(self):

        username1 = self._get_random_username()
        password1 = self._get_random_data()

        username2 = self._get_random_username()
        password2 = self._get_random_data()

        response1 = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username1,
            'password': password1,
        })

        response2 = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username2,
            'password': password2,
        })

        user_id1 = response1.user_id
        self._approve(user_id1)

        user_id2 = response2.user_id
        self._approve(user_id2)

        response = self.post('/zato/sso/user/login', {
            'username': username1,
            'password': password1,
        })

        ust = response.ust

        name = self._get_random_data()
        value = self._get_random_data()
        expiration = 900

        self.post('/zato/sso/user/attr', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id2,
            'name': name,
            'value': value,
            'expiration': expiration
        })

        new_value = self._get_random_data()
        new_expiration = 123

        response = self.patch('/zato/sso/user/attr', {
            'ust': ust,
            'user_id': user_id2,
            'name': name,
            'value': new_value,
            'expiration': new_expiration
        }, False)

        self.assertEqual(response.status, status_code.error)
        self.assertEqual(response.sub_status, [status_code.auth.not_allowed])

# ################################################################################################################################

    def xtest_update_many(self):

        data = [
            {'name': self._get_random_data(), 'value': self._get_random_data()},
            {'name': self._get_random_data(), 'value': self._get_random_data()},
        ]

        response = self.post('/zato/sso/user/attr', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'data': data,
        })

        self.assertEqual(response.status, status_code.ok)

# ################################################################################################################################

    def xtest_update_many_already_exists(self):

        data = [
            {'name': self._get_random_data(), 'value': self._get_random_data()},
            {'name': self._get_random_data(), 'value': self._get_random_data()},
        ]

        response1 = self.post('/zato/sso/user/attr', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'data': data,
        })

        response2 = self.post('/zato/sso/user/attr', {
            'ust': self.ctx.super_user_ust,
            'user_id': self.ctx.super_user_id,
            'data': data,
        }, False)

        self.assertEqual(response1.status, status_code.ok)
        self.assertEqual(response2.status, status_code.error)
        self.assertListEqual(response2.sub_status, [status_code.attr.already_exists])

# ################################################################################################################################

    def xtest_update_many_for_another_user_by_super_user(self):

        username = self._get_random_username()
        password = self._get_random_data()

        response = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username,
            'password': password,
        })

        user_id = response.user_id
        self._approve(user_id)

        data = [
            {'name': self._get_random_data(), 'value': self._get_random_data()},
            {'name': self._get_random_data(), 'value': self._get_random_data()},
        ]

        response = self.post('/zato/sso/user/attr', {
            'ust': self.ctx.super_user_ust,
            'user_id': user_id,
            'data': data,
        })

        self.assertEqual(response.status, status_code.ok)

# ################################################################################################################################

    def xtest_update_for_another_user_by_regular_user(self):

        username1 = self._get_random_username()
        password1 = self._get_random_data()

        username2 = self._get_random_username()
        password2 = self._get_random_data()

        response1 = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username1,
            'password': password1,
        })

        response2 = self.post('/zato/sso/user', {
            'ust': self.ctx.super_user_ust,
            'username': username2,
            'password': password2,
        })

        user_id1 = response1.user_id
        self._approve(user_id1)

        user_id2 = response2.user_id
        self._approve(user_id2)

        response = self.post('/zato/sso/user/login', {
            'username': username1,
            'password': password1,
        })

        ust = response.ust

        data = [
            {'name': self._get_random_data(), 'value': self._get_random_data()},
            {'name': self._get_random_data(), 'value': self._get_random_data()},
        ]

        response = self.post('/zato/sso/user/attr', {
            'ust': ust,
            'user_id': user_id2,
            'data': data
        }, False)

        self.assertEqual(response.status, status_code.error)
        self.assertEqual(response.sub_status, [status_code.auth.not_allowed])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import TestCase
from uuid import uuid4

# Bunch
from bunch import Bunch, bunchify

# nose
from nose.tools import eq_

# Python 2/3 compatibility
from future.utils import iteritems

# Zato
from zato.common import DATA_FORMAT, MISC, URL_TYPE, ZATO_NONE
from zato.common.test import rand_string
from zato.common.util import new_cid, payload_from_request
from zato.server.connection.http_soap import Unauthorized, url_data as url_data_mod
from zato.url_dispatcher import Matcher

# ################################################################################################################################

class DummyLock(object):
    def __init__(self):
        self.enter_called = False

    def __enter__(self):
        self.enter_called = True

    def __exit__(self, *ignored_args):
        pass

# ################################################################################################################################

class Dummy_update_basic_auth(object):
    def __call__(self, name, msg):
        self.name = name
        self.msg = msg

Dummy_update_apikey = Dummy_update_wss = Dummy_update_ntlm = Dummy_update_basic_auth

# ################################################################################################################################

class Dummy_update_url_sec(object):
    def __call__(self, msg, security_def_type, delete=False):
        self.msg = msg
        self.security_def_type = security_def_type
        self.delete = delete

# ################################################################################################################################

class Dummy_delete_channel_data(object):
    def __call__(self, security_def_type, name):
        self.security_def_type = security_def_type
        self.name = name

# ################################################################################################################################

class Dummy_delete_channel(object):
    def __init__(self, msg=None):
        self.msg = msg

    def __call__(self, msg, *args):
        self.msg = msg

Dummy_create_channel = Dummy_delete_channel

# ################################################################################################################################

dummy_worker = bunchify({
    'server': {
        'fs_server_config': {
            'rbac': {
                'auth_type_hook': None
            }
        }
    }
})

# ################################################################################################################################

class URLDataTestCase(TestCase):

    def test_match(self):
        url_data = url_data_mod.URLData(dummy_worker, [])

        soap_action1 = uuid4().hex.decode('utf-8')
        url_path1 = uuid4().hex.decode('utf-8')
        match_target1 = '{}{}{}'.format(soap_action1, MISC.SEPARATOR, url_path1)

        soap_action2 = uuid4().hex.decode('utf-8')
        url_path2 = uuid4().hex.decode('utf-8')
        match_target2 = '{}{}{}'.format(soap_action2, MISC.SEPARATOR, url_path2)

        soap_action3 = ''
        url_path3 = '/customer/{cid}/order/{oid}'
        match_target3 = '{}{}{}'.format(soap_action3, MISC.SEPARATOR, url_path3)

        item1 = Bunch()
        item1.name = 'name-2'
        item1.match_target = match_target1
        item1.match_target_compiled = Matcher(item1.match_target)

        item2 = Bunch()
        item2.name = 'name-1'
        item2.match_target = match_target2
        item2.match_target_compiled = Matcher(item2.match_target)

        item3 = Bunch()
        item3.name = 'name-3'
        item3.match_target = match_target3
        item3.match_target_compiled = Matcher(item3.match_target)

        # Note that we append in the order the 'name' attribute dictates
        # because .channel_data is a sorted list.
        url_data.channel_data.append(dict(item2))
        url_data.channel_data.append(dict(item1))
        url_data.channel_data.append(dict(item3))

        match, item_bunch = url_data.match(url_path1, soap_action1, True)
        eq_(match, {})
        eq_(item_bunch, item1)

        match, item_bunch = url_data.match(url_path2, soap_action2, True)
        eq_(match, {})
        eq_(item_bunch, item2)

        match, item_bunch = url_data.match('/customer/123/order/456', soap_action3, True)
        eq_(match, {})
        eq_(item_bunch, item3)

        match, _ = url_data.match('/foo/bar', '', False)
        self.assertIsNone(match)

# ################################################################################################################################

    def test_match_greedy(self):

        url_data = url_data_mod.URLData(dummy_worker, [])

        soap_action1 = ''
        url_path1 = '/customer/{cid}'
        match_target1 = '{}{}{}'.format(soap_action1, MISC.SEPARATOR, url_path1)

        soap_action2 = ''
        url_path2 = '/customer/{cid}/order/{oid}'
        match_target2 = '{}{}{}'.format(soap_action2, MISC.SEPARATOR, url_path2)

        soap_action3 = 'aaabbbccc'
        url_path3 = '/customer/{cid}/order'
        match_target3 = '{}{}{}'.format(soap_action3, MISC.SEPARATOR, url_path3)

        item1 = Bunch()
        item1.name = 'name-1'
        item1.match_target = match_target1
        item1.match_target_compiled = Matcher(item1.match_target)

        item2 = Bunch()
        item2.name = 'name-2'
        item2.match_target = match_target2
        item2.match_target_compiled = Matcher(item2.match_target)

        item3 = Bunch()
        item3.name = 'name-3'
        item3.match_target = match_target3
        item3.match_target_compiled = Matcher(item3.match_target)

        url_data.channel_data.append(dict(item1))
        url_data.channel_data.append(dict(item2))
        url_data.channel_data.append(dict(item3))

        match, info = url_data.match('/customer/123/order/456', '', False)
        eq_(sorted(match.items()), [])
        eq_(info.match_target, ':::/customer/{cid}/order/{oid}')
        eq_(sorted(info.match_target_compiled.group_names), ['cid','oid'])
        eq_(info.match_target_compiled.pattern, ':::/customer/{cid}/order/{oid}')
        eq_(
            info.match_target_compiled.matcher.pattern,
            ':::/customer/(?P<cid>[a-zA-Z0-9 _\\$.\\-|=~^]+)/order/(?P<oid>[a-zA-Z0-9 _\\$.\\-|=~^]+)$')

        match, info = url_data.match('/customer/abc', '', False)
        eq_(sorted(match.items()), [])
        eq_(info.match_target, ':::/customer/{cid}')
        eq_(sorted(info.match_target_compiled.group_names), ['cid'])
        eq_(info.match_target_compiled.pattern, ':::/customer/{cid}')
        eq_(info.match_target_compiled.matcher.pattern, ':::/customer/(?P<cid>[a-zA-Z0-9 _\\$.\\-|=~^]+)$')

        match, info = url_data.match('/customer/QWERTY/order', 'aaabbbccc', True)
        eq_(sorted(match.items()), [])
        eq_(info.match_target, 'aaabbbccc:::/customer/{cid}/order')
        eq_(sorted(info.match_target_compiled.group_names), ['cid'])
        eq_(info.match_target_compiled.pattern, 'aaabbbccc:::/customer/{cid}/order')
        eq_(info.match_target_compiled.matcher.pattern, 'aaabbbccc:::/customer/(?P<cid>[a-zA-Z0-9 _\\$.\\-|=~^]+)/order$')

# ################################################################################################################################

    def test_match_non_ascii(self):

        for elem in '_$.-|=~^abcdefABCDEF':

            cid = 'abc{}def'.format(elem)

            url_data = url_data_mod.URLData(dummy_worker, [])

            soap_action1 = ''
            url_path1 = '/customer/{cid}'
            match_target1 = '{}{}{}'.format(soap_action1, MISC.SEPARATOR, url_path1)

            item1 = Bunch()
            item1.name = 'name-1'
            item1.match_target = match_target1
            item1.match_target_compiled = Matcher(item1.match_target)

            url_data.channel_data.append(dict(item1))

            match, info = url_data.match('/customer/{}'.format(cid), '', False)
            self.assertDictEqual(match, {})

            eq_(sorted(match.items()), [])
            eq_(info.match_target, ':::/customer/{cid}')
            eq_(sorted(info.match_target_compiled.group_names), ['cid'])
            eq_(info.match_target_compiled.pattern, ':::/customer/{cid}')
            eq_(info.match_target_compiled.matcher.pattern, ':::/customer/(?P<cid>[a-zA-Z0-9 _\\$.\\-|=~^]+)$')

# ################################################################################################################################

    def test_match_whitespace(self):
        """ GH #505 HTTP channels do not take whitespace into account
        https://github.com/zatosource/zato/issues/505
        """
        url_data = url_data_mod.URLData(dummy_worker, [])

        soap_action3 = ''
        url_path3 = '/customer/{cid}/order/{oid}'
        match_target3 = '{}{}{}'.format(soap_action3, MISC.SEPARATOR, url_path3)

        item3 = Bunch()
        item3.name = 'name-3'
        item3.match_target = match_target3
        item3.match_target_compiled = Matcher(item3.match_target)

        url_data.channel_data.append(dict(item3))

        match, _ = url_data.match('/customer/1 23/order/4 56', soap_action3, True)
        eq_(sorted(match.items()), [])

# ################################################################################################################################

    def test_check_security(self):

        match_target1 = uuid4().hex

        class DummyMatch(object):
            def __init__(self, match_target):
                self.match_target = match_target

            def __getitem__(self, key):
                return False

            def get(self, ignored):
                return False

        class DummySecWrapper(object):
            def __init__(self, sec_def):
                self.sec_def = sec_def
                self.sec_use_rbac = False

        class DummySecDef(object):
            sec_type = 'basic_auth'

            def __getitem__(self, key):
                return object.__getattribute__(self, key)

        class DummyBasicAuth:
            def __init__(self):
                self.cid = ZATO_NONE
                self.sec_def = ZATO_NONE
                self.path_info = ZATO_NONE
                self.payload = ZATO_NONE
                self.wsgi_environ = ZATO_NONE

            def __call__(self, cid, sec_def, path_info, payload, wsgi_environ, post_data, enforce_auth):
                self.cid = cid
                self.sec_def = sec_def
                self.path_info = path_info
                self.payload = payload
                self.wsgi_environ = wsgi_environ
                self.post_data = post_data
                self.enforce_auth = enforce_auth

        dummy_basic_auth = DummyBasicAuth()

        expected_cid = uuid4().hex
        expected_path_info = uuid4().hex
        expected_payload = uuid4().hex
        expected_wsgi_environ = uuid4().hex
        expected_post_data = uuid4().hex

        match1 = DummyMatch(match_target1)
        sec_def1 = DummySecDef()
        wrapper1 = DummySecWrapper(sec_def1)

        url_sec = {
            match_target1: wrapper1,
        }

        url_data = url_data_mod.URLData(dummy_worker, [], url_sec=url_sec)
        url_data._handle_security_basic_auth = dummy_basic_auth

        url_data.check_security(
            wrapper1, expected_cid, match1, expected_path_info,
            expected_payload, expected_wsgi_environ, expected_post_data, None)

        eq_(dummy_basic_auth.cid, expected_cid)
        eq_(dummy_basic_auth.sec_def, sec_def1)
        eq_(dummy_basic_auth.path_info, expected_path_info)
        eq_(dummy_basic_auth.payload, expected_payload)
        eq_(dummy_basic_auth.wsgi_environ, expected_wsgi_environ)
        eq_(dummy_basic_auth.post_data, expected_post_data)

        dummy_basic_auth = DummyBasicAuth()

        url_data = url_data_mod.URLData(dummy_worker, [], url_sec=url_sec)
        url_data._handle_security_basic_auth = dummy_basic_auth

        eq_(dummy_basic_auth.cid, ZATO_NONE)
        eq_(dummy_basic_auth.sec_def, ZATO_NONE)
        eq_(dummy_basic_auth.path_info, ZATO_NONE)
        eq_(dummy_basic_auth.payload, ZATO_NONE)
        eq_(dummy_basic_auth.wsgi_environ, ZATO_NONE)

# ################################################################################################################################

    def test_update_url_sec(self):

        for name_attr in('name', 'old_name'):

            target_match1 = uuid4().hex
            target_match2 = uuid4().hex

            sec_def_name1 = uuid4().hex
            sec_def_name2 = uuid4().hex

            url_info1 = Bunch()
            url_info1.sec_def = Bunch()
            url_info1.sec_def.name = sec_def_name1
            url_info1.sec_def.sec_type = 'basic_auth'
            url_info1.sec_def.key1 = uuid4().hex
            url_info1.sec_def.key2 = uuid4().hex
            url_info1.sec_def.key3 = uuid4().hex

            url_info2 = Bunch()
            url_info2.sec_def = Bunch()
            url_info2.sec_def.name = sec_def_name2
            url_info2.sec_def.sec_type = 'basic_auth'

            url_sec = {
                target_match1: url_info1,
                target_match2: url_info2,
            }

            url_data = url_data_mod.URLData(dummy_worker, [], url_sec=url_sec)

            msg_attrs = {
                'key1': uuid4().hex,
                'key2': uuid4().hex,
                'key3': uuid4().hex,
                'unexisting-key': uuid4().hex # Note it doesn't exist in url_info1
            }

            msg = Bunch()
            msg[name_attr] = sec_def_name1

            for attr in msg_attrs:
                msg[attr] = msg_attrs[attr]

            url_data._update_url_sec(msg, 'basic_auth')

            ud_url_info1 = url_data.url_sec[target_match1]

            eq_(ud_url_info1.sec_def.key1, msg['key1'])
            eq_(ud_url_info1.sec_def.key2, msg['key2'])
            eq_(ud_url_info1.sec_def.key3, msg['key3'])
            self.assertNotIn('unexisting-key', ud_url_info1.sec_def)

            ud_url_info2 = url_data.url_sec[target_match2]

            self.assertNotIn('key1', ud_url_info2.sec_def)
            self.assertNotIn('key2', ud_url_info2.sec_def)
            self.assertNotIn('key3', ud_url_info2.sec_def)
            self.assertNotIn('unexisting-key', ud_url_info2.sec_def)

            url_data = url_data_mod.URLData(dummy_worker, [], url_sec=url_sec)
            url_data._update_url_sec(msg, 'basic_auth', True)

            try:
                url_data.url_sec[target_match1]
            except KeyError:
                pass
            else:
                self.fail('Expected KeyError here, {} should have been deleted'.format(
                    target_match1))

            ud_url_info2 = url_data.url_sec[target_match2]

            self.assertNotIn('key1', ud_url_info2.sec_def)
            self.assertNotIn('key2', ud_url_info2.sec_def)
            self.assertNotIn('key3', ud_url_info2.sec_def)
            self.assertNotIn('unexisting-key', ud_url_info2.sec_def)

# ################################################################################################################################

    def test_delete_channel_data(self):

        sec1 = Bunch()
        sec1.name = uuid4().hex
        sec1.sec_type = uuid4().hex
        sec1.security_name = uuid4().hex
        sec1.is_internal = False

        sec2 = Bunch()
        sec2.name = uuid4().hex
        sec2.sec_type = uuid4().hex
        sec2.security_name = uuid4().hex
        sec2.is_internal = False

        url_data = url_data_mod.URLData(dummy_worker, channel_data=[sec1, sec2])
        eq_(len(url_data.channel_data), 2)

        url_data._delete_channel_data(sec1.sec_type, sec1.security_name)
        eq_(len(url_data.channel_data), 1)

        channel_data = url_data.channel_data[0]
        eq_(channel_data.sec_type, sec2.sec_type)
        eq_(channel_data.security_name, sec2.security_name)

        url_data._delete_channel_data(uuid4().hex, uuid4().hex)
        eq_(len(url_data.channel_data), 1)

        # Still the same
        channel_data = url_data.channel_data[0]
        eq_(channel_data.sec_type, sec2.sec_type)
        eq_(channel_data.security_name, sec2.security_name)

# ################################################################################################################################

    def test_update_basic_auth(self):
        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.basic_auth_config = {}

        name1 = uuid4().hex

        value1 = uuid4().hex
        value2 = uuid4().hex

        config1 = {
            'value1': value1,
            'value2': value2,
        }

        url_data._update_basic_auth(name1, config1)

        eq_(len(url_data.basic_auth_config), 1)
        self.assertTrue(name1 in url_data.basic_auth_config)
        eq_(sorted(url_data.basic_auth_config[name1].config.items()), [(u'value1', value1), (u'value2', value2)])

# ################################################################################################################################

    def test_handle_security_apikey(self):
        username, password = uuid4().hex, uuid4().hex
        url_data = url_data_mod.URLData(dummy_worker, [])
        cid = new_cid()
        sec_def = Bunch(username=username, password=password)
        path_info = '/'
        body = ''

        # No header at that point
        wsgi_environ = {}

        try:
            url_data._handle_security_apikey(cid, sec_def, path_info, body, wsgi_environ)
        except Unauthorized:
            pass
        else:
            self.fail('No header sent, expected Unauthorized')

        # Correct header name but invalid key
        wsgi_environ[username] = uuid4().hex

        try:
            url_data._handle_security_apikey(cid, sec_def, path_info, body, wsgi_environ)
        except Unauthorized:
            pass
        else:
            self.fail('Invalid key, expected Unauthorized')

        # Both header and key are valid, not exception at this point
        wsgi_environ[username] = password

        url_data._handle_security_apikey(cid, sec_def, path_info, body, wsgi_environ)

# ################################################################################################################################

    def test_handle_security_xpath_sec(self):

        test_data = [
            [True, rand_string(), rand_string()],
            [False, rand_string(), rand_string()],
            [True, rand_string(), None],
            [False, rand_string(), None]
        ]

        username_expr = "//*[local-name()='mydoc']/@user"
        for is_valid, valid_username, password in test_data:

            password_expr = "//*[local-name()='mydoc']/@password" if password else None
            xml_username = valid_username if is_valid else rand_string()

            cid = rand_string()
            url_data = url_data_mod.URLData(dummy_worker, [])
            sec_def = Bunch(username=valid_username, password=password, username_expr=username_expr, password_expr=password_expr)

            xml = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:foo="http://foo.example.com">
                <soapenv:Header/>
                <soapenv:Body>
                  <foo:mydoc user="{}" password="{}"/>
                </soapenv:Body>
                </soapenv:Envelope>""".format(xml_username, password)

            payload = payload_from_request(cid, xml, DATA_FORMAT.XML, URL_TYPE.SOAP)

            if is_valid:
                result = url_data._handle_security_xpath_sec(cid, sec_def, None, None, {'zato.request.payload':payload})
                self.assertEqual(result, True)
            else:
                try:
                    url_data._handle_security_xpath_sec(cid, sec_def, None, None, {'zato.request.payload':payload})
                except Unauthorized:
                    pass
                else:
                    self.fail('Expected Unauthorized, `{}`, `{}`, `{}`, `{}`, `{}`'.format(
                        is_valid, valid_username, xml_username, password, xml))

# ################################################################################################################################

    def test_apikey_get(self):

        name1, value1 = uuid4().hex, uuid4().hex

        dummy_lock = DummyLock()

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.url_sec_lock = dummy_lock
        url_data.apikey_config = {name1: value1}

        value = url_data.apikey_get(name1)
        eq_(value, value1)
        eq_(dummy_lock.enter_called, True)

        value = url_data.apikey_get(uuid4().hex)
        eq_(value, None)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_APIKEY_CREATE(self):

        dummy_lock = DummyLock()
        dummy_update_apikey = Dummy_update_apikey()

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.url_sec_lock = dummy_lock
        url_data._update_apikey = dummy_update_apikey

        msg = Bunch()
        msg.name = uuid4().hex
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex

        url_data.on_broker_msg_SECURITY_APIKEY_CREATE(msg)

        eq_(dummy_lock.enter_called, True)
        eq_(dummy_update_apikey.name, msg.name)
        eq_(dummy_update_apikey.msg.key1, msg.key1)
        eq_(dummy_update_apikey.msg.key2, msg.key2)
        eq_(dummy_update_apikey.msg.key3, msg.key3)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_APIKEY_EDIT(self):

        dummy_lock = DummyLock()
        dummy_update_apikey = Dummy_update_apikey()
        dummy_update_url_sec = Dummy_update_url_sec()

        old_name = uuid4().hex

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.apikey_config = {old_name: uuid4().hex}
        url_data.url_sec_lock = dummy_lock
        url_data._update_apikey = dummy_update_apikey
        url_data._update_url_sec = dummy_update_url_sec

        msg = Bunch()
        msg.old_name = old_name
        msg.name = uuid4().hex
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex

        url_data.on_broker_msg_SECURITY_APIKEY_EDIT(msg)

        eq_(dummy_lock.enter_called, True)

        eq_(dummy_update_apikey.name, msg.name)
        eq_(dummy_update_apikey.msg.key1, msg.key1)
        eq_(dummy_update_apikey.msg.key2, msg.key2)
        eq_(dummy_update_apikey.msg.key3, msg.key3)

        eq_(dummy_update_url_sec.msg.old_name, msg.old_name)
        eq_(dummy_update_url_sec.msg.name, msg.name)
        eq_(dummy_update_url_sec.msg.key1, msg.key1)
        eq_(dummy_update_url_sec.msg.key2, msg.key2)
        eq_(dummy_update_url_sec.msg.key3, msg.key3)
        eq_(dummy_update_url_sec.security_def_type, 'apikey')
        eq_(dummy_update_url_sec.delete, False)

        self.assertNotIn(old_name, url_data.apikey_config)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_APIKEY_DELETE(self):

        dummy_lock = DummyLock()
        dummy_update_apikey = Dummy_update_apikey()
        dummy_update_url_sec = Dummy_update_url_sec()
        dummy_delete_channel_data = Dummy_delete_channel_data()

        name = uuid4().hex

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.apikey_config = {name: uuid4().hex}
        url_data.url_sec_lock = dummy_lock
        url_data._update_apikey = dummy_update_apikey
        url_data._update_url_sec = dummy_update_url_sec
        url_data._delete_channel_data = dummy_delete_channel_data

        msg = Bunch()
        msg.name = name
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex

        url_data.on_broker_msg_SECURITY_APIKEY_DELETE(msg)

        eq_(dummy_lock.enter_called, True)

        eq_(dummy_update_url_sec.msg.name, msg.name)
        eq_(dummy_update_url_sec.msg.key1, msg.key1)
        eq_(dummy_update_url_sec.msg.key2, msg.key2)
        eq_(dummy_update_url_sec.msg.key3, msg.key3)
        eq_(dummy_update_url_sec.security_def_type, 'apikey')
        eq_(dummy_update_url_sec.delete, True)

        self.assertNotIn(name, url_data.apikey_config)

        eq_(dummy_delete_channel_data.name, name)
        eq_(dummy_delete_channel_data.security_def_type, 'apikey')

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_APIKEY_CHANGE_PASSWORD(self):

        dummy_lock = DummyLock()
        dummy_update_url_sec = Dummy_update_url_sec()

        name = uuid4().hex
        old_password = uuid4().hex
        new_pasword = uuid4().hex

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.apikey_config = {name: {'config':{'password':old_password}}}
        url_data.url_sec_lock = dummy_lock
        url_data._update_url_sec = dummy_update_url_sec

        msg = Bunch()
        msg.name = name
        msg.password = new_pasword
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex

        url_data.on_broker_msg_SECURITY_APIKEY_CHANGE_PASSWORD(msg)

        eq_(dummy_lock.enter_called, True)

        eq_(dummy_update_url_sec.msg.name, msg.name)
        eq_(dummy_update_url_sec.msg.key1, msg.key1)
        eq_(dummy_update_url_sec.msg.key2, msg.key2)
        eq_(dummy_update_url_sec.msg.key3, msg.key3)
        eq_(dummy_update_url_sec.security_def_type, 'apikey')
        eq_(dummy_update_url_sec.delete, False)

        eq_(url_data.apikey_config[name]['config']['password'], new_pasword)

# ################################################################################################################################

    def test_basic_auth_get(self):

        name1, value1 = uuid4().hex, uuid4().hex

        dummy_lock = DummyLock()

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.url_sec_lock = dummy_lock
        url_data.basic_auth_config = {name1: value1}

        value = url_data.basic_auth_get(name1)
        eq_(value, value1)
        eq_(dummy_lock.enter_called, True)

        value = url_data.basic_auth_get(uuid4().hex)
        eq_(value, None)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE(self):

        dummy_lock = DummyLock()
        dummy_update_basic_auth = Dummy_update_basic_auth()

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.url_sec_lock = dummy_lock
        url_data._update_basic_auth = dummy_update_basic_auth

        msg = Bunch()
        msg.name = uuid4().hex
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex

        url_data.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        eq_(dummy_lock.enter_called, True)
        eq_(dummy_update_basic_auth.name, msg.name)
        eq_(dummy_update_basic_auth.msg.key1, msg.key1)
        eq_(dummy_update_basic_auth.msg.key2, msg.key2)
        eq_(dummy_update_basic_auth.msg.key3, msg.key3)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_EDIT(self):

        dummy_lock = DummyLock()
        dummy_update_basic_auth = Dummy_update_basic_auth()
        dummy_update_url_sec = Dummy_update_url_sec()

        old_name = uuid4().hex

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.basic_auth_config = {old_name: uuid4().hex}
        url_data.url_sec_lock = dummy_lock
        url_data._update_basic_auth = dummy_update_basic_auth
        url_data._update_url_sec = dummy_update_url_sec

        msg = Bunch()
        msg.old_name = old_name
        msg.name = uuid4().hex
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex

        url_data.on_broker_msg_SECURITY_BASIC_AUTH_EDIT(msg)

        eq_(dummy_lock.enter_called, True)

        eq_(dummy_update_basic_auth.name, msg.name)
        eq_(dummy_update_basic_auth.msg.key1, msg.key1)
        eq_(dummy_update_basic_auth.msg.key2, msg.key2)
        eq_(dummy_update_basic_auth.msg.key3, msg.key3)

        eq_(dummy_update_url_sec.msg.old_name, msg.old_name)
        eq_(dummy_update_url_sec.msg.name, msg.name)
        eq_(dummy_update_url_sec.msg.key1, msg.key1)
        eq_(dummy_update_url_sec.msg.key2, msg.key2)
        eq_(dummy_update_url_sec.msg.key3, msg.key3)
        eq_(dummy_update_url_sec.security_def_type, 'basic_auth')
        eq_(dummy_update_url_sec.delete, False)

        self.assertNotIn(old_name, url_data.basic_auth_config)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_DELETE(self):

        dummy_lock = DummyLock()
        dummy_update_basic_auth = Dummy_update_basic_auth()
        dummy_update_url_sec = Dummy_update_url_sec()
        dummy_delete_channel_data = Dummy_delete_channel_data()

        name = uuid4().hex

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.basic_auth_config = {name: uuid4().hex}
        url_data.url_sec_lock = dummy_lock
        url_data._update_basic_auth = dummy_update_basic_auth
        url_data._update_url_sec = dummy_update_url_sec
        url_data._delete_channel_data = dummy_delete_channel_data

        msg = Bunch()
        msg.name = name
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex

        url_data.on_broker_msg_SECURITY_BASIC_AUTH_DELETE(msg)

        eq_(dummy_lock.enter_called, True)

        eq_(dummy_update_url_sec.msg.name, msg.name)
        eq_(dummy_update_url_sec.msg.key1, msg.key1)
        eq_(dummy_update_url_sec.msg.key2, msg.key2)
        eq_(dummy_update_url_sec.msg.key3, msg.key3)
        eq_(dummy_update_url_sec.security_def_type, 'basic_auth')
        eq_(dummy_update_url_sec.delete, True)

        self.assertNotIn(name, url_data.basic_auth_config)

        eq_(dummy_delete_channel_data.name, name)
        eq_(dummy_delete_channel_data.security_def_type, 'basic_auth')

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(self):

        dummy_lock = DummyLock()
        dummy_update_url_sec = Dummy_update_url_sec()

        name = uuid4().hex
        old_password = uuid4().hex
        new_pasword = uuid4().hex

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.basic_auth_config = {name: {'config':{'password':old_password}}}
        url_data.url_sec_lock = dummy_lock
        url_data._update_url_sec = dummy_update_url_sec

        msg = Bunch()
        msg.name = name
        msg.password = new_pasword
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex

        url_data.on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(msg)

        eq_(dummy_lock.enter_called, True)

        eq_(dummy_update_url_sec.msg.name, msg.name)
        eq_(dummy_update_url_sec.msg.key1, msg.key1)
        eq_(dummy_update_url_sec.msg.key2, msg.key2)
        eq_(dummy_update_url_sec.msg.key3, msg.key3)
        eq_(dummy_update_url_sec.security_def_type, 'basic_auth')
        eq_(dummy_update_url_sec.delete, False)

        eq_(url_data.basic_auth_config[name]['config']['password'], new_pasword)

# ################################################################################################################################

    def test_update_ntlm(self):
        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.ntlm_config = {}

        name1 = uuid4().hex

        value1 = uuid4().hex
        value2 = uuid4().hex

        config1 = {
            'value1': value1,
            'value2': value2,
        }

        url_data._update_ntlm(name1, config1)

        eq_(len(url_data.ntlm_config), 1)
        self.assertTrue(name1 in url_data.ntlm_config)
        eq_(sorted(url_data.ntlm_config[name1].config.items()), [(u'value1', value1), (u'value2', value2)])

# ################################################################################################################################

    def test_ntlm_get(self):

        name1, value1 = uuid4().hex, uuid4().hex

        dummy_lock = DummyLock()

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.url_sec_lock = dummy_lock
        url_data.ntlm_config = {name1: value1}

        value = url_data.ntlm_get(name1)
        eq_(value, value1)
        eq_(dummy_lock.enter_called, True)

        value = url_data.ntlm_get(uuid4().hex)
        eq_(value, None)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_NTLM_CREATE(self):

        dummy_lock = DummyLock()
        dummy_update_ntlm = Dummy_update_ntlm()

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.url_sec_lock = dummy_lock
        url_data._update_ntlm = dummy_update_ntlm

        msg = Bunch()
        msg.name = uuid4().hex
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex

        url_data.on_broker_msg_SECURITY_NTLM_CREATE(msg)

        eq_(dummy_lock.enter_called, True)
        eq_(dummy_update_ntlm.name, msg.name)
        eq_(dummy_update_ntlm.msg.key1, msg.key1)
        eq_(dummy_update_ntlm.msg.key2, msg.key2)
        eq_(dummy_update_ntlm.msg.key3, msg.key3)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_NTLM_EDIT(self):

        dummy_lock = DummyLock()
        dummy_update_ntlm = Dummy_update_ntlm()
        dummy_update_url_sec = Dummy_update_url_sec()

        old_name = uuid4().hex

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.ntlm_config = {old_name: uuid4().hex}
        url_data.url_sec_lock = dummy_lock
        url_data._update_ntlm = dummy_update_ntlm
        url_data._update_url_sec = dummy_update_url_sec

        msg = Bunch()
        msg.old_name = old_name
        msg.name = uuid4().hex
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex

        url_data.on_broker_msg_SECURITY_NTLM_EDIT(msg)

        eq_(dummy_lock.enter_called, True)

        eq_(dummy_update_ntlm.name, msg.name)
        eq_(dummy_update_ntlm.msg.key1, msg.key1)
        eq_(dummy_update_ntlm.msg.key2, msg.key2)
        eq_(dummy_update_ntlm.msg.key3, msg.key3)

        eq_(dummy_update_url_sec.msg.old_name, msg.old_name)
        eq_(dummy_update_url_sec.msg.name, msg.name)
        eq_(dummy_update_url_sec.msg.key1, msg.key1)
        eq_(dummy_update_url_sec.msg.key2, msg.key2)
        eq_(dummy_update_url_sec.msg.key3, msg.key3)
        eq_(dummy_update_url_sec.security_def_type, 'ntlm')
        eq_(dummy_update_url_sec.delete, False)

        self.assertNotIn(old_name, url_data.ntlm_config)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_NTLM_DELETE(self):

        dummy_lock = DummyLock()
        dummy_update_ntlm = Dummy_update_ntlm()
        dummy_update_url_sec = Dummy_update_url_sec()
        dummy_delete_channel_data = Dummy_delete_channel_data()

        name = uuid4().hex

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.ntlm_config = {name: uuid4().hex}
        url_data.url_sec_lock = dummy_lock
        url_data._update_ntlm = dummy_update_ntlm
        url_data._update_url_sec = dummy_update_url_sec
        url_data._delete_channel_data = dummy_delete_channel_data

        msg = Bunch()
        msg.name = name
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex

        url_data.on_broker_msg_SECURITY_NTLM_DELETE(msg)

        eq_(dummy_lock.enter_called, True)

        eq_(dummy_update_url_sec.msg.name, msg.name)
        eq_(dummy_update_url_sec.msg.key1, msg.key1)
        eq_(dummy_update_url_sec.msg.key2, msg.key2)
        eq_(dummy_update_url_sec.msg.key3, msg.key3)
        eq_(dummy_update_url_sec.security_def_type, 'ntlm')
        eq_(dummy_update_url_sec.delete, True)

        self.assertNotIn(name, url_data.ntlm_config)

        eq_(dummy_delete_channel_data.name, name)
        eq_(dummy_delete_channel_data.security_def_type, 'ntlm')

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_NTLM_CHANGE_PASSWORD(self):

        dummy_lock = DummyLock()
        dummy_update_url_sec = Dummy_update_url_sec()

        name = uuid4().hex
        old_password = uuid4().hex
        new_pasword = uuid4().hex

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.ntlm_config = {name: {'config':{'password':old_password}}}
        url_data.url_sec_lock = dummy_lock
        url_data._update_url_sec = dummy_update_url_sec

        msg = Bunch()
        msg.name = name
        msg.password = new_pasword
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex

        url_data.on_broker_msg_SECURITY_NTLM_CHANGE_PASSWORD(msg)

        eq_(dummy_lock.enter_called, True)

        eq_(dummy_update_url_sec.msg.name, msg.name)
        eq_(dummy_update_url_sec.msg.key1, msg.key1)
        eq_(dummy_update_url_sec.msg.key2, msg.key2)
        eq_(dummy_update_url_sec.msg.key3, msg.key3)
        eq_(dummy_update_url_sec.security_def_type, 'ntlm')
        eq_(dummy_update_url_sec.delete, False)

        eq_(url_data.ntlm_config[name]['config']['password'], new_pasword)

# ################################################################################################################################

    def test_update_wss(self):
        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.wss_config = {}

        name1 = uuid4().hex

        value1 = uuid4().hex
        value2 = uuid4().hex

        config1 = {
            'value1': value1,
            'value2': value2,
        }

        url_data._update_wss(name1, config1)

        eq_(len(url_data.wss_config), 1)
        self.assertTrue(name1 in url_data.wss_config)
        eq_(sorted(url_data.wss_config[name1].config.items()), [(u'value1', value1), (u'value2', value2)])

# ################################################################################################################################

    def test_wss_get(self):

        name1, value1 = uuid4().hex, uuid4().hex

        dummy_lock = DummyLock()

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.url_sec_lock = dummy_lock
        url_data.wss_config = {name1: value1}

        value = url_data.wss_get(name1)
        eq_(value, value1)
        eq_(dummy_lock.enter_called, True)

        value = url_data.wss_get(uuid4().hex)
        eq_(value, None)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_WSS_CREATE(self):

        dummy_lock = DummyLock()
        dummy_update_wss = Dummy_update_wss()

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.url_sec_lock = dummy_lock
        url_data._update_wss = dummy_update_wss

        msg = Bunch()
        msg.name = uuid4().hex
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex

        url_data.on_broker_msg_SECURITY_WSS_CREATE(msg)

        eq_(dummy_lock.enter_called, True)
        eq_(dummy_update_wss.name, msg.name)
        eq_(dummy_update_wss.msg.key1, msg.key1)
        eq_(dummy_update_wss.msg.key2, msg.key2)
        eq_(dummy_update_wss.msg.key3, msg.key3)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_WSS_EDIT(self):

        dummy_lock = DummyLock()
        dummy_update_wss = Dummy_update_wss()
        dummy_update_url_sec = Dummy_update_url_sec()

        old_name = uuid4().hex

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.wss_config = {old_name: uuid4().hex}
        url_data.url_sec_lock = dummy_lock
        url_data._update_wss = dummy_update_wss
        url_data._update_url_sec = dummy_update_url_sec

        msg = Bunch()
        msg.old_name = old_name
        msg.name = uuid4().hex
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex

        url_data.on_broker_msg_SECURITY_WSS_EDIT(msg)

        eq_(dummy_lock.enter_called, True)

        eq_(dummy_update_wss.name, msg.name)
        eq_(dummy_update_wss.msg.key1, msg.key1)
        eq_(dummy_update_wss.msg.key2, msg.key2)
        eq_(dummy_update_wss.msg.key3, msg.key3)

        eq_(dummy_update_url_sec.msg.old_name, msg.old_name)
        eq_(dummy_update_url_sec.msg.name, msg.name)
        eq_(dummy_update_url_sec.msg.key1, msg.key1)
        eq_(dummy_update_url_sec.msg.key2, msg.key2)
        eq_(dummy_update_url_sec.msg.key3, msg.key3)
        eq_(dummy_update_url_sec.security_def_type, 'wss')
        eq_(dummy_update_url_sec.delete, False)

        self.assertNotIn(old_name, url_data.wss_config)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_WSS_DELETE(self):

        dummy_lock = DummyLock()
        dummy_update_wss = Dummy_update_wss()
        dummy_update_url_sec = Dummy_update_url_sec()
        dummy_delete_channel_data = Dummy_delete_channel_data()

        name = uuid4().hex

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.wss_config = {name: uuid4().hex}
        url_data.url_sec_lock = dummy_lock
        url_data._update_wss = dummy_update_wss
        url_data._update_url_sec = dummy_update_url_sec
        url_data._delete_channel_data = dummy_delete_channel_data

        msg = Bunch()
        msg.name = name
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex

        url_data.on_broker_msg_SECURITY_WSS_DELETE(msg)

        eq_(dummy_lock.enter_called, True)

        eq_(dummy_update_url_sec.msg.name, msg.name)
        eq_(dummy_update_url_sec.msg.key1, msg.key1)
        eq_(dummy_update_url_sec.msg.key2, msg.key2)
        eq_(dummy_update_url_sec.msg.key3, msg.key3)
        eq_(dummy_update_url_sec.security_def_type, 'wss')
        eq_(dummy_update_url_sec.delete, True)

        self.assertNotIn(name, url_data.wss_config)

        eq_(dummy_delete_channel_data.name, name)
        eq_(dummy_delete_channel_data.security_def_type, 'wss')

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_WSS_CHANGE_PASSWORD(self):

        dummy_lock = DummyLock()
        dummy_update_url_sec = Dummy_update_url_sec()

        name = uuid4().hex
        old_password = uuid4().hex
        new_pasword = uuid4().hex

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.wss_config = {name: {'config':{'password':old_password}}}
        url_data.url_sec_lock = dummy_lock
        url_data._update_url_sec = dummy_update_url_sec

        msg = Bunch()
        msg.name = name
        msg.password = new_pasword
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex

        url_data.on_broker_msg_SECURITY_WSS_CHANGE_PASSWORD(msg)

        eq_(dummy_lock.enter_called, True)

        eq_(dummy_update_url_sec.msg.name, msg.name)
        eq_(dummy_update_url_sec.msg.key1, msg.key1)
        eq_(dummy_update_url_sec.msg.key2, msg.key2)
        eq_(dummy_update_url_sec.msg.key3, msg.key3)
        eq_(dummy_update_url_sec.security_def_type, 'wss')
        eq_(dummy_update_url_sec.delete, False)

        eq_(url_data.wss_config[name]['config']['password'], new_pasword)

# ################################################################################################################################

    def test_channel_item_from_msg(self):

        def get_msg(needs_security_id):
            msg = {}

            for name in('connection', 'data_format', 'has_rbac', 'host', 'id', 'is_active', 'is_internal', 'method', 'name',
                'ping_method', 'pool_size', 'service_id', 'impl_name', 'service_name', 'soap_action', 'soap_version',
                'transport', 'url_path', 'merge_url_params_req', 'url_params_pri', 'params_pri', 'content_type'):
                msg[name] = uuid4().hex

            msg['sec_use_rbac'] = False
            msg['cache_type'] = None
            msg['cache_id'] = None
            msg['cache_name'] = None
            msg['cache_expiry'] = None

            if needs_security_id:
                for name in('sec_type', 'security_id', 'security_name'):
                    msg[name] = uuid4().hex

            return msg

# ################################################################################################################################

        def check_channel_item(match_target, msg, channel_item, needs_security_id):

            eq_(channel_item['service_impl_name'], msg['impl_name'])
            eq_(channel_item['match_target'], match_target)

            for name in('connection', 'data_format', 'has_rbac', 'host', 'id', 'is_active',
                'is_internal', 'method', 'name', 'ping_method', 'pool_size',
                'service_id', 'impl_name', 'service_name',
                'soap_action', 'soap_version', 'transport', 'url_path',
                'merge_url_params_req', 'url_params_pri', 'params_pri'):
                eq_(msg[name], channel_item[name])

            if needs_security_id:
                eq_(len(channel_item.keys()), 38)
                for name in('sec_type', 'security_id', 'security_name'):
                    eq_(msg[name], channel_item[name])
            else:
                eq_(len(channel_item.keys()), 35)

        for needs_security_id in(True, False):
            msg = get_msg(needs_security_id)
            match_target = uuid4().hex.decode('utf-8')
            channel_item = url_data_mod.URLData(dummy_worker, [])._channel_item_from_msg(msg, match_target)
            check_channel_item(match_target, msg, channel_item, needs_security_id)

# ################################################################################################################################

    def test_sec_info_from_msg(self):

        security_name = uuid4().hex
        basic_auth_config = {
            security_name: {'config':{uuid4().hex:uuid4().hex, uuid4().hex:uuid4().hex}}
        }

        for sec_name in(None, security_name):

            msg = Bunch()
            msg.id = 1
            msg.security_name = security_name
            msg.sec_type = 'basic_auth'
            msg.is_active = uuid4().hex
            msg.data_format = uuid4().hex
            msg.transport = uuid4().hex
            msg.sec_use_rbac = False

            url_data = url_data_mod.URLData(dummy_worker, [])
            url_data.basic_auth_config = basic_auth_config

            sec_info = url_data._sec_info_from_msg(msg)

            eq_(sec_info.is_active, msg.is_active)
            eq_(sec_info.data_format, msg.data_format)
            eq_(sec_info.transport, msg.transport)

            if msg.security_name:
                for k, v in iteritems(basic_auth_config[security_name]['config']):
                    eq_(sec_info.sec_def[k], v)
            else:
                eq_(sec_info.sec_def, ZATO_NONE)

# ################################################################################################################################

    def test_create_channel(self):

        channel_item = {'name':uuid4().hex, 'is_internal':False}
        sec_info = uuid4().hex
        soap_action = uuid4().hex
        url_path = uuid4().hex
        match_target = '{}{}{}'.format(soap_action, MISC.SEPARATOR, url_path)

        def _dummy_channel_item_from_msg(*ignored):
            return channel_item

        def _dummy_sec_info_from_msg(*ignored):
            return sec_info

        msg = Bunch()
        msg.soap_action = soap_action
        msg.url_path = url_path

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data._channel_item_from_msg = _dummy_channel_item_from_msg
        url_data._sec_info_from_msg = _dummy_sec_info_from_msg
        url_data.url_sec = {}

        url_data._create_channel(msg, {})

        self.assertIn(match_target, url_data.url_sec)
        eq_(url_data.url_sec[match_target], sec_info)

        eq_(len(url_data.channel_data), 1)
        eq_(url_data.channel_data[0], channel_item)

# ################################################################################################################################

    def test_delete_channel(self):

        old_soap_action = uuid4().hex
        old_url_path = uuid4().hex

        item1 = Bunch()
        item1.match_target = uuid4().hex
        item1.name = uuid4().hex
        item1.is_internal = False

        item2 = Bunch()
        item2.match_target = '{}{}{}'.format(old_soap_action, MISC.SEPARATOR, old_url_path)
        item2.name = uuid4().hex
        item2.is_internal = False

        item3 = Bunch()
        item3.match_target = uuid4().hex
        item3.name = uuid4().hex
        item3.is_internal = False

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.channel_data = [item1, item2, item3]

        url_data.url_sec = {}
        for item in url_data.channel_data:
            url_data.url_sec[item.match_target] = uuid4().hex

        msg = Bunch()
        msg.old_soap_action = old_soap_action
        msg.old_url_path = old_url_path

        url_data._delete_channel(msg)

        self.assertNotIn(item2, url_data.channel_data)
        self.assertNotIn(item2.match_target, url_data.url_sec)

# ################################################################################################################################

    def test_on_broker_msg_CHANNEL_HTTP_SOAP_CREATE_EDIT(self):

        no_old_name_msg = uuid4().hex
        dummy_lock = DummyLock()
        dummy_delete_channel = Dummy_delete_channel(no_old_name_msg)
        dummy_create_channel = Dummy_create_channel()

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.url_sec_lock = dummy_lock
        url_data._delete_channel = dummy_delete_channel
        url_data._create_channel = dummy_create_channel

        old_name = uuid4().hex
        key = uuid4().hex
        value = uuid4().hex

        for _old_name in(None, old_name):
            msg = Bunch()
            msg.old_name = old_name
            msg[key] = value

            url_data.on_broker_msg_CHANNEL_HTTP_SOAP_CREATE_EDIT(msg)

            if msg.old_name:
                eq_(dummy_delete_channel.msg.old_name, msg.old_name)
                eq_(dummy_delete_channel.msg[key], msg[key])
            else:
                eq_(dummy_delete_channel.msg, no_old_name_msg)

            eq_(sorted(dummy_create_channel.msg.items()), sorted(msg.items()))
            eq_(dummy_lock.enter_called, True)

# ################################################################################################################################

    def test_on_broker_msg_CHANNEL_HTTP_SOAP_DELETE(self):

        dummy_lock = DummyLock()
        dummy_delete_channel = Dummy_delete_channel()

        url_data = url_data_mod.URLData(dummy_worker, [])
        url_data.url_sec_lock = dummy_lock
        url_data._delete_channel = dummy_delete_channel

        key1 = uuid4().hex
        value1 = uuid4().hex

        key2 = uuid4().hex
        value2 = uuid4().hex

        msg = Bunch()
        msg[key1] = value1
        msg[key2] = value2

        url_data.on_broker_msg_CHANNEL_HTTP_SOAP_DELETE(msg)

        eq_(dummy_delete_channel.msg[key1], msg[key1])
        eq_(dummy_delete_channel.msg[key2], msg[key2])

        eq_(dummy_lock.enter_called, True)

# ################################################################################################################################

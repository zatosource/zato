# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from cStringIO import StringIO
from unittest import TestCase
from uuid import uuid4

# Bunch
from bunch import Bunch

# nose
from nose.tools import eq_

# parse
from parse import compile as parse_compile, Result

# Zato
from zato.common import MISC, ZATO_NONE
from zato.server.connection.http_soap import url_data

class DummyLock(object):
    def __init__(self):
        self.enter_called = False
        
    def __enter__(self):
        self.enter_called = True
        
    def __exit__(self, *ignored_args):
        pass
    
class Dummy_update_basic_auth(object):
    def __call__(self, name, msg):
        self.name = name
        self.msg = msg

Dummy_update_wss = Dummy_update_tech_acc = Dummy_update_basic_auth  
        
class Dummy_update_url_sec(object):
    def __call__(self, msg, security_def_type, delete=False):
        self.msg = msg
        self.security_def_type = security_def_type
        self.delete = delete
        
class Dummy_delete_channel_data(object):
    def __call__(self, security_def_type, name):
        self.security_def_type = security_def_type
        self.name = name

# ##############################################################################

class URLDataTestCase(TestCase):
    
    def test_match(self):
        ud = url_data.URLData([])

        soap_action1 = uuid4().hex
        url_path1 = uuid4().hex
        match_target1 = '{}{}{}'.format(soap_action1, MISC.SEPARATOR, url_path1)
        
        soap_action2 = uuid4().hex
        url_path2 = uuid4().hex
        match_target2 = '{}{}{}'.format(soap_action2, MISC.SEPARATOR, url_path2)
        
        soap_action3 = ''
        url_path3 = '/customer/{cid}/order/{oid}'
        match_target3 = '{}{}{}'.format(soap_action3, MISC.SEPARATOR, url_path3)
        
        item1 = Bunch()
        item1.match_target = match_target1
        item1.match_target_compiled = parse_compile(item1.match_target)
        
        item2 = Bunch()
        item2.match_target = match_target2
        item2.match_target_compiled = parse_compile(item2.match_target)
        
        item3 = Bunch()
        item3.match_target = match_target3
        item3.match_target_compiled = parse_compile(item3.match_target)
        
        ud.channel_data.append(item1)
        ud.channel_data.append(item2)
        ud.channel_data.append(item3)
        
        match = ud.match(url_path1, soap_action1)
        self.assertIsInstance(match, Result)
        eq_(match.named, {})
        eq_(match.spans, {})
        
        match = ud.match(url_path2, soap_action2)
        self.assertIsInstance(match, Result)
        eq_(match.named, {})
        eq_(match.spans, {})
        
        match = ud.match('/customer/123/order/456', soap_action3)
        self.assertIsInstance(match, Result)
        eq_(sorted(match.named.items()), [(u'cid', u'123'), (u'oid', u'456')])
        eq_(sorted(match.spans.items()), [(u'cid', (13, 16)), (u'oid', (23, 26))])
        
        match = ud.match('/foo/bar', '')
        self.assertIsNone(match)

# ##############################################################################

    def test_check_security(self):
        
        match_target1 = uuid4().hex
        match_target2 = uuid4().hex
        
        class DummyMatch(object):
            def __init__(self, match_target):
                self.match_target = match_target

        class DummySecWrapper(object):
            def __init__(self, sec_def):
                self.sec_def = sec_def
                
        class DummySecDef(object):
            sec_type = 'basic_auth'
            
        class DummyBasicAuth:
            def __init__(self):
                self.cid = ZATO_NONE
                self.sec_def = ZATO_NONE
                self.path_info = ZATO_NONE
                self.payload = ZATO_NONE
                self.wsgi_environ = ZATO_NONE
                
            def __call__(self, cid, sec_def, path_info, payload, wsgi_environ):
                self.cid = cid
                self.sec_def = sec_def
                self.path_info = path_info
                self.payload = payload
                self.wsgi_environ = wsgi_environ
                
        # ######################################################################
                
        dummy_basic_auth = DummyBasicAuth()

        expected_cid = uuid4().hex
        expected_path_info = uuid4().hex
        expected_payload = uuid4().hex
        expected_wsgi_environ = uuid4().hex
        
        match1 = DummyMatch(match_target1)
        match2 = DummyMatch(match_target2)
        
        sec_def1 = DummySecDef()
        
        wrapper1 = DummySecWrapper(sec_def1)
        wrapper2 = DummySecWrapper(ZATO_NONE)
        
        
        url_sec = {
            match_target1: wrapper1,
            match_target2: wrapper2
        }
        
        ud = url_data.URLData(url_sec=url_sec)
        ud._handle_security_basic_auth = dummy_basic_auth
        
        ud.check_security(
            expected_cid, match1, expected_path_info, expected_payload, expected_wsgi_environ)
        
        eq_(dummy_basic_auth.cid, expected_cid)
        eq_(dummy_basic_auth.sec_def, sec_def1)
        eq_(dummy_basic_auth.path_info, expected_path_info)
        eq_(dummy_basic_auth.payload, expected_payload)
        eq_(dummy_basic_auth.wsgi_environ, expected_wsgi_environ)
        
        # ######################################################################
        
        dummy_basic_auth = DummyBasicAuth()
        
        ud = url_data.URLData(url_sec=url_sec)
        ud._handle_security_basic_auth = dummy_basic_auth
        
        ud.check_security(
            expected_cid, match2, expected_path_info, expected_payload, expected_wsgi_environ)
        
        eq_(dummy_basic_auth.cid, ZATO_NONE)
        eq_(dummy_basic_auth.sec_def, ZATO_NONE)
        eq_(dummy_basic_auth.path_info, ZATO_NONE)
        eq_(dummy_basic_auth.payload, ZATO_NONE)
        eq_(dummy_basic_auth.wsgi_environ, ZATO_NONE)
        
# ##############################################################################

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
        
            ud = url_data.URLData(url_sec=url_sec)
            
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
                
            ud._update_url_sec(msg, 'basic_auth')
            
            ud_url_info1 = ud.url_sec[target_match1]
            
            eq_(ud_url_info1.sec_def.key1, msg['key1'])
            eq_(ud_url_info1.sec_def.key2, msg['key2'])
            eq_(ud_url_info1.sec_def.key3, msg['key3'])
            self.assertNotIn('unexisting-key', ud_url_info1.sec_def)
            
            ud_url_info2 = ud.url_sec[target_match2]
            
            self.assertNotIn('key1', ud_url_info2.sec_def)
            self.assertNotIn('key2', ud_url_info2.sec_def)
            self.assertNotIn('key3', ud_url_info2.sec_def)
            self.assertNotIn('unexisting-key', ud_url_info2.sec_def)
            
            # ######################################################################
            
            ud = url_data.URLData(url_sec=url_sec)
            ud._update_url_sec(msg, 'basic_auth', True)
            
            try:
                ud.url_sec[target_match1]
            except KeyError:
                pass
            else:
                self.fail('Expected KeyError here, {} should have been deleted'.format(
                    target_match1))
                
            ud_url_info2 = ud.url_sec[target_match2]
            
            self.assertNotIn('key1', ud_url_info2.sec_def)
            self.assertNotIn('key2', ud_url_info2.sec_def)
            self.assertNotIn('key3', ud_url_info2.sec_def)
            self.assertNotIn('unexisting-key', ud_url_info2.sec_def)
            
# ##############################################################################

    def test_delete_channel_data(self):
        
        sec1 = Bunch()
        sec1.sec_type = uuid4().hex
        sec1.security_name = uuid4().hex

        sec2 = Bunch()
        sec2.sec_type = uuid4().hex
        sec2.security_name = uuid4().hex
        
        ud = url_data.URLData(channel_data=[sec1, sec2])
        eq_(len(ud.channel_data), 2)
        
        ud._delete_channel_data(sec1.sec_type, sec1.security_name)
        eq_(len(ud.channel_data), 1)
        
        channel_data = ud.channel_data[0]
        eq_(channel_data.sec_type, sec2.sec_type)
        eq_(channel_data.security_name, sec2.security_name)
        
        ud._delete_channel_data(uuid4().hex, uuid4().hex)
        eq_(len(ud.channel_data), 1)
        
        # Still the same
        channel_data = ud.channel_data[0]
        eq_(channel_data.sec_type, sec2.sec_type)
        eq_(channel_data.security_name, sec2.security_name)

# ##############################################################################
        
    def test_update_basic_auth(self):
        ud = url_data.URLData()
        ud.basic_auth_config = {}
        
        name1 = uuid4().hex
        name2 = uuid4().hex
        
        value1 = uuid4().hex
        value2 = uuid4().hex
        
        config1 = {
            'value1': value1,
            'value2': value2,
        }
        
        ud._update_basic_auth(name1, config1)
        
        eq_(len(ud.basic_auth_config), 1)
        self.assertTrue(name1 in ud.basic_auth_config)
        eq_(sorted(ud.basic_auth_config[name1].config.items()), [(u'value1', value1), (u'value2', value2)])
        
    def test_basic_auth_get(self):
        
        name1, value1 = uuid4().hex, uuid4().hex
        
        dummy_lock = DummyLock()
        
        ud = url_data.URLData()
        ud.url_sec_lock = dummy_lock
        ud.basic_auth_config = {name1: value1}
        
        value = ud.basic_auth_get(name1)
        eq_(value, value1)
        eq_(dummy_lock.enter_called, True)

        value = ud.basic_auth_get(uuid4().hex)
        eq_(value, None)
        
    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE(self):
        
        dummy_lock = DummyLock()
        dummy_update_basic_auth = Dummy_update_basic_auth()
        
        ud = url_data.URLData()
        ud.url_sec_lock = dummy_lock
        ud._update_basic_auth = dummy_update_basic_auth
        
        msg = Bunch()
        msg.name = uuid4().hex
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex
        
        ud.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)
        
        eq_(dummy_lock.enter_called, True)
        eq_(dummy_update_basic_auth.name, msg.name)
        eq_(dummy_update_basic_auth.msg.key1, msg.key1)
        eq_(dummy_update_basic_auth.msg.key2, msg.key2)
        eq_(dummy_update_basic_auth.msg.key3, msg.key3)

    def test_on_broker_msg_SECURITY_BASIC_AUTH_EDIT(self):
        
        dummy_lock = DummyLock()
        dummy_update_basic_auth = Dummy_update_basic_auth()
        dummy_update_url_sec = Dummy_update_url_sec()
        
        old_name = uuid4().hex
        
        ud = url_data.URLData()
        ud.basic_auth_config = {old_name: uuid4().hex}
        ud.url_sec_lock = dummy_lock
        ud._update_basic_auth = dummy_update_basic_auth
        ud._update_url_sec = dummy_update_url_sec
        
        msg = Bunch()
        msg.old_name = old_name
        msg.name = uuid4().hex
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex
        
        ud.on_broker_msg_SECURITY_BASIC_AUTH_EDIT(msg)
        
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

        self.assertNotIn(old_name, ud.basic_auth_config)
        
    def test_on_broker_msg_SECURITY_BASIC_AUTH_DELETE(self):
        
        dummy_lock = DummyLock()
        dummy_update_basic_auth = Dummy_update_basic_auth()
        dummy_update_url_sec = Dummy_update_url_sec()
        dummy_delete_channel_data = Dummy_delete_channel_data()
        
        name = uuid4().hex
        
        ud = url_data.URLData()
        ud.basic_auth_config = {name: uuid4().hex}
        ud.url_sec_lock = dummy_lock
        ud._update_basic_auth = dummy_update_basic_auth
        ud._update_url_sec = dummy_update_url_sec
        ud._delete_channel_data = dummy_delete_channel_data
        
        msg = Bunch()
        msg.name = name
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex
        
        ud.on_broker_msg_SECURITY_BASIC_AUTH_DELETE(msg)
        
        eq_(dummy_lock.enter_called, True)
        
        eq_(dummy_update_url_sec.msg.name, msg.name)
        eq_(dummy_update_url_sec.msg.key1, msg.key1)
        eq_(dummy_update_url_sec.msg.key2, msg.key2)
        eq_(dummy_update_url_sec.msg.key3, msg.key3)
        eq_(dummy_update_url_sec.security_def_type, 'basic_auth')
        eq_(dummy_update_url_sec.delete, True)

        self.assertNotIn(name, ud.basic_auth_config)
        
        eq_(dummy_delete_channel_data.name, name)
        eq_(dummy_delete_channel_data.security_def_type, 'basic_auth')

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(self):
        
        dummy_lock = DummyLock()
        dummy_update_url_sec = Dummy_update_url_sec()
        
        name = uuid4().hex
        old_pasword = uuid4().hex
        new_pasword = uuid4().hex
        
        ud = url_data.URLData()
        ud.basic_auth_config = {name: {'config':{'password':old_pasword}}}
        ud.url_sec_lock = dummy_lock
        ud._update_url_sec = dummy_update_url_sec
        
        msg = Bunch()
        msg.name = name
        msg.password = new_pasword
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex
        
        ud.on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(msg)
        
        eq_(dummy_lock.enter_called, True)
        
        eq_(dummy_update_url_sec.msg.name, msg.name)
        eq_(dummy_update_url_sec.msg.key1, msg.key1)
        eq_(dummy_update_url_sec.msg.key2, msg.key2)
        eq_(dummy_update_url_sec.msg.key3, msg.key3)
        eq_(dummy_update_url_sec.security_def_type, 'basic_auth')
        eq_(dummy_update_url_sec.delete, False)
        
        eq_(ud.basic_auth_config[name]['config']['password'], new_pasword)

# ##############################################################################

    def test_update_tech_acc(self):
        ud = url_data.URLData()
        ud.tech_acc_config = {}
        
        name1 = uuid4().hex
        name2 = uuid4().hex
        
        value1 = uuid4().hex
        value2 = uuid4().hex
        
        config1 = {
            'value1': value1,
            'value2': value2,
        }
        
        ud._update_tech_acc(name1, config1)
        
        eq_(len(ud.tech_acc_config), 1)
        self.assertTrue(name1 in ud.tech_acc_config)
        eq_(sorted(ud.tech_acc_config[name1].config.items()), [(u'value1', value1), (u'value2', value2)])
        
    def test_tech_acc_get(self):
        
        name1, value1 = uuid4().hex, uuid4().hex
        
        dummy_lock = DummyLock()
        
        ud = url_data.URLData()
        ud.url_sec_lock = dummy_lock
        ud.tech_acc_config = {name1: value1}
        
        value = ud.tech_acc_get(name1)
        eq_(value, value1)
        eq_(dummy_lock.enter_called, True)

        value = ud.tech_acc_get(uuid4().hex)
        eq_(value, None)
        
    def test_on_broker_msg_SECURITY_TECH_ACC_CREATE(self):
        
        dummy_lock = DummyLock()
        dummy_update_tech_acc = Dummy_update_tech_acc()
        
        ud = url_data.URLData()
        ud.url_sec_lock = dummy_lock
        ud._update_tech_acc = dummy_update_tech_acc
        
        msg = Bunch()
        msg.name = uuid4().hex
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex
        
        ud.on_broker_msg_SECURITY_TECH_ACC_CREATE(msg)
        
        eq_(dummy_lock.enter_called, True)
        eq_(dummy_update_tech_acc.name, msg.name)
        eq_(dummy_update_tech_acc.msg.key1, msg.key1)
        eq_(dummy_update_tech_acc.msg.key2, msg.key2)
        eq_(dummy_update_tech_acc.msg.key3, msg.key3)

    def test_on_broker_msg_SECURITY_TECH_ACC_EDIT(self):
        
        dummy_lock = DummyLock()
        dummy_update_tech_acc = Dummy_update_tech_acc()
        dummy_update_url_sec = Dummy_update_url_sec()
        
        old_name = uuid4().hex
        
        ud = url_data.URLData()
        ud.tech_acc_config = {old_name: uuid4().hex}
        ud.url_sec_lock = dummy_lock
        ud._update_tech_acc = dummy_update_tech_acc
        ud._update_url_sec = dummy_update_url_sec
        
        msg = Bunch()
        msg.old_name = old_name
        msg.name = uuid4().hex
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex
        
        ud.on_broker_msg_SECURITY_TECH_ACC_EDIT(msg)
        
        eq_(dummy_lock.enter_called, True)
        
        eq_(dummy_update_tech_acc.name, msg.name)
        eq_(dummy_update_tech_acc.msg.key1, msg.key1)
        eq_(dummy_update_tech_acc.msg.key2, msg.key2)
        eq_(dummy_update_tech_acc.msg.key3, msg.key3)
        
        eq_(dummy_update_url_sec.msg.old_name, msg.old_name)
        eq_(dummy_update_url_sec.msg.name, msg.name)
        eq_(dummy_update_url_sec.msg.key1, msg.key1)
        eq_(dummy_update_url_sec.msg.key2, msg.key2)
        eq_(dummy_update_url_sec.msg.key3, msg.key3)
        eq_(dummy_update_url_sec.security_def_type, 'tech_acc')
        eq_(dummy_update_url_sec.delete, False)

        self.assertNotIn(old_name, ud.tech_acc_config)
        
    def test_on_broker_msg_SECURITY_TECH_ACC_DELETE(self):
        
        dummy_lock = DummyLock()
        dummy_update_tech_acc = Dummy_update_tech_acc()
        dummy_update_url_sec = Dummy_update_url_sec()
        dummy_delete_channel_data = Dummy_delete_channel_data()
        
        name = uuid4().hex
        
        ud = url_data.URLData()
        ud.tech_acc_config = {name: uuid4().hex}
        ud.url_sec_lock = dummy_lock
        ud._update_tech_acc = dummy_update_tech_acc
        ud._update_url_sec = dummy_update_url_sec
        ud._delete_channel_data = dummy_delete_channel_data
        
        msg = Bunch()
        msg.name = name
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex
        
        ud.on_broker_msg_SECURITY_TECH_ACC_DELETE(msg)
        
        eq_(dummy_lock.enter_called, True)
        
        eq_(dummy_update_url_sec.msg.name, msg.name)
        eq_(dummy_update_url_sec.msg.key1, msg.key1)
        eq_(dummy_update_url_sec.msg.key2, msg.key2)
        eq_(dummy_update_url_sec.msg.key3, msg.key3)
        eq_(dummy_update_url_sec.security_def_type, 'tech_acc')
        eq_(dummy_update_url_sec.delete, True)

        self.assertNotIn(name, ud.tech_acc_config)
        
        eq_(dummy_delete_channel_data.name, name)
        eq_(dummy_delete_channel_data.security_def_type, 'tech_acc')

    def test_on_broker_msg_SECURITY_TECH_ACC_CHANGE_PASSWORD(self):
        
        dummy_lock = DummyLock()
        dummy_update_url_sec = Dummy_update_url_sec()
        
        name = uuid4().hex
        old_pasword = uuid4().hex
        new_pasword = uuid4().hex
        
        ud = url_data.URLData()
        ud.tech_acc_config = {name: {'config':{'password':old_pasword}}}
        ud.url_sec_lock = dummy_lock
        ud._update_url_sec = dummy_update_url_sec
        
        msg = Bunch()
        msg.name = name
        msg.password = new_pasword
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex
        
        ud.on_broker_msg_SECURITY_TECH_ACC_CHANGE_PASSWORD(msg)
        
        eq_(dummy_lock.enter_called, True)
        
        eq_(dummy_update_url_sec.msg.name, msg.name)
        eq_(dummy_update_url_sec.msg.key1, msg.key1)
        eq_(dummy_update_url_sec.msg.key2, msg.key2)
        eq_(dummy_update_url_sec.msg.key3, msg.key3)
        eq_(dummy_update_url_sec.security_def_type, 'tech_acc')
        eq_(dummy_update_url_sec.delete, False)
        
        eq_(ud.tech_acc_config[name]['config']['password'], new_pasword)
        
    # ##############################################################################
    
    def test_update_wss(self):
        ud = url_data.URLData()
        ud.wss_config = {}
        
        name1 = uuid4().hex
        name2 = uuid4().hex
        
        value1 = uuid4().hex
        value2 = uuid4().hex
        
        config1 = {
            'value1': value1,
            'value2': value2,
        }
        
        ud._update_wss(name1, config1)
        
        eq_(len(ud.wss_config), 1)
        self.assertTrue(name1 in ud.wss_config)
        eq_(sorted(ud.wss_config[name1].config.items()), [(u'value1', value1), (u'value2', value2)])
        
    def test_wss_get(self):
        
        name1, value1 = uuid4().hex, uuid4().hex
        
        dummy_lock = DummyLock()
        
        ud = url_data.URLData()
        ud.url_sec_lock = dummy_lock
        ud.wss_config = {name1: value1}
        
        value = ud.wss_get(name1)
        eq_(value, value1)
        eq_(dummy_lock.enter_called, True)

        value = ud.wss_get(uuid4().hex)
        eq_(value, None)
        
    def test_on_broker_msg_SECURITY_WSS_CREATE(self):
        
        dummy_lock = DummyLock()
        dummy_update_wss = Dummy_update_wss()
        
        ud = url_data.URLData()
        ud.url_sec_lock = dummy_lock
        ud._update_wss = dummy_update_wss
        
        msg = Bunch()
        msg.name = uuid4().hex
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex
        
        ud.on_broker_msg_SECURITY_WSS_CREATE(msg)
        
        eq_(dummy_lock.enter_called, True)
        eq_(dummy_update_wss.name, msg.name)
        eq_(dummy_update_wss.msg.key1, msg.key1)
        eq_(dummy_update_wss.msg.key2, msg.key2)
        eq_(dummy_update_wss.msg.key3, msg.key3)

    def test_on_broker_msg_SECURITY_WSS_EDIT(self):
        
        dummy_lock = DummyLock()
        dummy_update_wss = Dummy_update_wss()
        dummy_update_url_sec = Dummy_update_url_sec()
        
        old_name = uuid4().hex
        
        ud = url_data.URLData()
        ud.wss_config = {old_name: uuid4().hex}
        ud.url_sec_lock = dummy_lock
        ud._update_wss = dummy_update_wss
        ud._update_url_sec = dummy_update_url_sec
        
        msg = Bunch()
        msg.old_name = old_name
        msg.name = uuid4().hex
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex
        
        ud.on_broker_msg_SECURITY_WSS_EDIT(msg)
        
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

        self.assertNotIn(old_name, ud.wss_config)
        
    def test_on_broker_msg_SECURITY_WSS_DELETE(self):
        
        dummy_lock = DummyLock()
        dummy_update_wss = Dummy_update_wss()
        dummy_update_url_sec = Dummy_update_url_sec()
        dummy_delete_channel_data = Dummy_delete_channel_data()
        
        name = uuid4().hex
        
        ud = url_data.URLData()
        ud.wss_config = {name: uuid4().hex}
        ud.url_sec_lock = dummy_lock
        ud._update_wss = dummy_update_wss
        ud._update_url_sec = dummy_update_url_sec
        ud._delete_channel_data = dummy_delete_channel_data
        
        msg = Bunch()
        msg.name = name
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex
        
        ud.on_broker_msg_SECURITY_WSS_DELETE(msg)
        
        eq_(dummy_lock.enter_called, True)
        
        eq_(dummy_update_url_sec.msg.name, msg.name)
        eq_(dummy_update_url_sec.msg.key1, msg.key1)
        eq_(dummy_update_url_sec.msg.key2, msg.key2)
        eq_(dummy_update_url_sec.msg.key3, msg.key3)
        eq_(dummy_update_url_sec.security_def_type, 'wss')
        eq_(dummy_update_url_sec.delete, True)

        self.assertNotIn(name, ud.wss_config)
        
        eq_(dummy_delete_channel_data.name, name)
        eq_(dummy_delete_channel_data.security_def_type, 'wss')

    def test_on_broker_msg_SECURITY_WSS_CHANGE_PASSWORD(self):
        
        dummy_lock = DummyLock()
        dummy_update_url_sec = Dummy_update_url_sec()
        
        name = uuid4().hex
        old_pasword = uuid4().hex
        new_pasword = uuid4().hex
        
        ud = url_data.URLData()
        ud.wss_config = {name: {'config':{'password':old_pasword}}}
        ud.url_sec_lock = dummy_lock
        ud._update_url_sec = dummy_update_url_sec
        
        msg = Bunch()
        msg.name = name
        msg.password = new_pasword
        msg.key1 = uuid4().hex
        msg.key2 = uuid4().hex
        msg.key3 = uuid4().hex
        
        ud.on_broker_msg_SECURITY_WSS_CHANGE_PASSWORD(msg)
        
        eq_(dummy_lock.enter_called, True)
        
        eq_(dummy_update_url_sec.msg.name, msg.name)
        eq_(dummy_update_url_sec.msg.key1, msg.key1)
        eq_(dummy_update_url_sec.msg.key2, msg.key2)
        eq_(dummy_update_url_sec.msg.key3, msg.key3)
        eq_(dummy_update_url_sec.security_def_type, 'wss')
        eq_(dummy_update_url_sec.delete, False)
        
        eq_(ud.wss_config[name]['config']['password'], new_pasword)
            
# ##############################################################################

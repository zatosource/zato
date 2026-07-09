# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from unittest import main, TestCase
from unittest.mock import patch

# Bunch
from zato.common.ext.bunch import Bunch, bunchify

# Zato
from zato.server.config import ConfigDict
from zato.server.connection.facade import RESTFacade, RESTInvoker

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    CID = 'abc-123'
    Conn_Name = 'CRM and Billing'
    Conn_Name_FS = 'CRM_and_Billing'
    Conn_Name_Exact = 'ExactNameConn'
    Conn_Name_Prefixed = 'MyPrefix.Payments'
    Name_Prefix = 'MyPrefix.'
    Env_Key_Conn_Name = 'Zato_Test_Facade_Conn_Name'
    No_Path_Given = '/zato-no-path-given'

# All the HTTP verbs that a RESTInvoker exposes, mapped to what the underlying wrapper receives
Invoker_Verbs = ['get', 'delete', 'options', 'post', 'put', 'patch', 'ping', 'upload']

# All the direct verbs on RESTFacade that map to the requests library
Facade_Direct_Verbs = ['delete', 'get', 'head', 'patch', 'post', 'put']

# ################################################################################################################################
# ################################################################################################################################

class _FakeHTTPSOAPWrapper:
    """ Stands in for HTTPSOAPWrapper - records each call so tests can assert on the exact arguments received.
    """
    def __init__(self, name:'str') -> 'None':
        self.config = {'name': name}
        self.calls = []

# ################################################################################################################################

    def _record(self, func_name:'str', *args:'any_', **kwargs:'any_') -> 'str':
        self.calls.append((func_name, args, kwargs))
        out = f'{func_name}-response'
        return out

# ################################################################################################################################

    def get(self, *args:'any_', **kwargs:'any_') -> 'str':
        return self._record('get', *args, **kwargs)

    def delete(self, *args:'any_', **kwargs:'any_') -> 'str':
        return self._record('delete', *args, **kwargs)

    def options(self, *args:'any_', **kwargs:'any_') -> 'str':
        return self._record('options', *args, **kwargs)

    def post(self, *args:'any_', **kwargs:'any_') -> 'str':
        return self._record('post', *args, **kwargs)

    def put(self, *args:'any_', **kwargs:'any_') -> 'str':
        return self._record('put', *args, **kwargs)

    def patch(self, *args:'any_', **kwargs:'any_') -> 'str':
        return self._record('patch', *args, **kwargs)

    def ping(self, *args:'any_', **kwargs:'any_') -> 'str':
        return self._record('ping', *args, **kwargs)

    def upload(self, *args:'any_', **kwargs:'any_') -> 'str':
        return self._record('upload', *args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

def get_out_plain_http() -> 'ConfigDict':
    """ Builds a ConfigDict shaped exactly like config_store.out_plain_http, i.e. each entry
    is a Bunch with a 'config' sub-Bunch and a 'conn' wrapper object.
    """
    out = ConfigDict('out_plain_http', Bunch())

    entries = [
        (ModuleCtx.Conn_Name, ModuleCtx.Conn_Name_FS),
        (ModuleCtx.Conn_Name_Exact, ModuleCtx.Conn_Name_Exact),
        (ModuleCtx.Conn_Name_Prefixed, ModuleCtx.Conn_Name_Prefixed),
    ]

    for name, name_fs_safe in entries:
        item = bunchify({
            'config': {
                'name': name,
                'name_fs_safe': name_fs_safe,
            },
        })
        item.conn = _FakeHTTPSOAPWrapper(name)
        out[name] = item

    return out

# ################################################################################################################################
# ################################################################################################################################

class _HooksRESTFacade(RESTFacade):
    """ A subclass with before/after hooks, following the same pattern as KeysightHawkeyeFacade.
    """
    def __init__(self) -> 'None':
        self.hook_calls = []

    def before_call_func(self, func_name:'str', conn_name:'str', conn:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        self.hook_calls.append(('before', func_name, conn_name, conn, args, kwargs))

    def after_call_func(self, func_name:'str', conn_name:'str', conn:'any_', result:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        self.hook_calls.append(('after', func_name, conn_name, conn, result, args, kwargs))

# ################################################################################################################################
# ################################################################################################################################

class _PathInArgsRESTFacade(RESTFacade):
    has_path_in_args = True

# ################################################################################################################################
# ################################################################################################################################

class _PrefixedRESTFacade(RESTFacade):
    name_prefix = ModuleCtx.Name_Prefix

# ################################################################################################################################
# ################################################################################################################################

class RESTFacadeTestCase(TestCase):

    def setUp(self) -> 'None':
        self.out_plain_http = get_out_plain_http()
        self.facade = RESTFacade()
        self.facade.init(ModuleCtx.CID, self.out_plain_http)

# ################################################################################################################################

    def get_wrapper(self, name:'str') -> '_FakeHTTPSOAPWrapper':
        out = self.out_plain_http[name].conn
        return out

# ################################################################################################################################

    def test_getitem_returns_invoker(self) -> 'None':

        conn = self.facade[ModuleCtx.Conn_Name]

        self.assertIsInstance(conn, RESTInvoker)
        self.assertIs(conn.conn, self.get_wrapper(ModuleCtx.Conn_Name))
        self.assertIs(conn.container, self.facade)

# ################################################################################################################################

    def test_getitem_unknown_name_raises_keyerror(self) -> 'None':

        with self.assertRaises(KeyError):
            _ = self.facade['No Such Connection']

# ################################################################################################################################

    def test_getitem_env_variable_name(self) -> 'None':

        os.environ[ModuleCtx.Env_Key_Conn_Name] = ModuleCtx.Conn_Name

        try:
            conn = self.facade['$' + ModuleCtx.Env_Key_Conn_Name]
            self.assertIs(conn.conn, self.get_wrapper(ModuleCtx.Conn_Name))
        finally:
            del os.environ[ModuleCtx.Env_Key_Conn_Name]

# ################################################################################################################################

    def test_getattr_exact_name(self) -> 'None':

        conn = self.facade.ExactNameConn

        self.assertIsInstance(conn, RESTInvoker)
        self.assertIs(conn.conn, self.get_wrapper(ModuleCtx.Conn_Name_Exact))

# ################################################################################################################################

    def test_getattr_fs_safe_name(self) -> 'None':

        conn = self.facade.CRM_and_Billing

        self.assertIsInstance(conn, RESTInvoker)
        self.assertIs(conn.conn, self.get_wrapper(ModuleCtx.Conn_Name))

# ################################################################################################################################

    def test_getattr_unknown_name_raises_keyerror(self) -> 'None':

        with self.assertRaises(KeyError):
            _ = self.facade.No_Such_Connection

# ################################################################################################################################

    def test_each_verb_injects_cid(self) -> 'None':

        for verb in Invoker_Verbs:

            wrapper = self.get_wrapper(ModuleCtx.Conn_Name)
            wrapper.calls.clear()

            conn = self.facade[ModuleCtx.Conn_Name]
            func = getattr(conn, verb)

            result = func('my-data', my_param='my-value')

            self.assertEqual(result, f'{verb}-response')
            self.assertEqual(wrapper.calls, [(verb, (ModuleCtx.CID, 'my-data'), {'my_param': 'my-value'})])

# ################################################################################################################################

    def test_send_is_alias_for_post(self) -> 'None':

        wrapper = self.get_wrapper(ModuleCtx.Conn_Name)
        conn = self.facade[ModuleCtx.Conn_Name]

        result = conn.send('my-data')

        self.assertEqual(result, 'post-response')
        self.assertEqual(wrapper.calls, [('post', (ModuleCtx.CID, 'my-data'), {})])

# ################################################################################################################################

    def test_explicit_cid_is_not_duplicated(self) -> 'None':

        wrapper = self.get_wrapper(ModuleCtx.Conn_Name)
        conn = self.facade[ModuleCtx.Conn_Name]

        _ = conn.post(ModuleCtx.CID, 'my-data')

        self.assertEqual(wrapper.calls, [('post', (ModuleCtx.CID, 'my-data'), {})])

# ################################################################################################################################

    def test_no_cid_given_injects_cid_once(self) -> 'None':

        wrapper = self.get_wrapper(ModuleCtx.Conn_Name)
        conn = self.facade[ModuleCtx.Conn_Name]

        _ = conn.post('my-data')

        self.assertEqual(wrapper.calls, [('post', (ModuleCtx.CID, 'my-data'), {})])

# ################################################################################################################################

    def test_invoker_conn_is_raw_wrapper(self) -> 'None':

        wrapper = self.get_wrapper(ModuleCtx.Conn_Name)
        conn = self.facade[ModuleCtx.Conn_Name]

        self.assertIs(conn.conn, wrapper)

        # Calling the wrapper directly, with an explicit CID, works as well
        _ = conn.conn.post(ModuleCtx.CID, 'my-data')

        self.assertEqual(wrapper.calls, [('post', (ModuleCtx.CID, 'my-data'), {})])

# ################################################################################################################################

    def test_out_rest_config_dict_access(self) -> 'None':

        # This is what self.out.rest[name].conn resolves to in a service
        wrapper = self.out_plain_http[ModuleCtx.Conn_Name].conn

        self.assertIs(wrapper, self.get_wrapper(ModuleCtx.Conn_Name))

        _ = wrapper.post(ModuleCtx.CID, 'my-data')

        self.assertEqual(wrapper.calls, [('post', (ModuleCtx.CID, 'my-data'), {})])

# ################################################################################################################################

    def test_out_rest_config_dict_unknown_name_raises_keyerror(self) -> 'None':

        with self.assertRaises(KeyError):
            _ = self.out_plain_http['No Such Connection']

# ################################################################################################################################

    def test_facade_direct_verbs_use_requests(self) -> 'None':

        for verb in Facade_Direct_Verbs:

            target = f'zato.server.connection.facade.requests_{verb}'

            with patch(target) as mock_func:
                mock_func.return_value = f'{verb}-requests-response'

                func = getattr(self.facade, verb)
                result = func('https://example.com', params={'my-key': 'my-value'})

                self.assertEqual(result, f'{verb}-requests-response')
                mock_func.assert_called_once_with('https://example.com', params={'my-key': 'my-value'})

        # No wrapper was invoked along the way
        for name in [ModuleCtx.Conn_Name, ModuleCtx.Conn_Name_Exact, ModuleCtx.Conn_Name_Prefixed]:
            self.assertEqual(self.get_wrapper(name).calls, [])

# ################################################################################################################################

    def test_repr_contains_conn_name(self) -> 'None':

        conn = self.facade[ModuleCtx.Conn_Name]

        self.assertIn('RESTInvoker', repr(conn))
        self.assertIn(ModuleCtx.Conn_Name, repr(conn))

# ################################################################################################################################
# ################################################################################################################################

class RESTFacadeHooksTestCase(TestCase):

    def setUp(self) -> 'None':
        self.out_plain_http = get_out_plain_http()
        self.facade = _HooksRESTFacade()
        self.facade.init(ModuleCtx.CID, self.out_plain_http)

# ################################################################################################################################

    def test_before_and_after_hooks_fire(self) -> 'None':

        wrapper = self.out_plain_http[ModuleCtx.Conn_Name].conn
        conn = self.facade[ModuleCtx.Conn_Name]

        result = conn.post('my-data', my_param='my-value')

        self.assertEqual(result, 'post-response')

        before_call, after_call = self.facade.hook_calls

        self.assertEqual(before_call, ('before', 'post', ModuleCtx.Conn_Name, wrapper, ('my-data',), {'my_param': 'my-value'}))
        self.assertEqual(
            after_call, ('after', 'post', ModuleCtx.Conn_Name, wrapper, 'post-response', ('my-data',), {'my_param': 'my-value'}))

# ################################################################################################################################
# ################################################################################################################################

class RESTFacadePathInArgsTestCase(TestCase):

    def setUp(self) -> 'None':
        self.out_plain_http = get_out_plain_http()
        self.facade = _PathInArgsRESTFacade()
        self.facade.init(ModuleCtx.CID, self.out_plain_http)

# ################################################################################################################################

    def test_path_moves_into_params(self) -> 'None':

        wrapper = self.out_plain_http[ModuleCtx.Conn_Name].conn
        conn = self.facade[ModuleCtx.Conn_Name]

        _ = conn.get('/my/path')

        self.assertEqual(wrapper.calls, [('get', (ModuleCtx.CID,), {'params': {'_zato_path': '/my/path'}})])

# ################################################################################################################################

    def test_no_path_given_uses_default(self) -> 'None':

        wrapper = self.out_plain_http[ModuleCtx.Conn_Name].conn
        conn = self.facade[ModuleCtx.Conn_Name]

        _ = conn.get()

        self.assertEqual(wrapper.calls, [('get', (ModuleCtx.CID,), {'params': {'_zato_path': ModuleCtx.No_Path_Given}})])

# ################################################################################################################################

    def test_path_preserves_existing_params(self) -> 'None':

        wrapper = self.out_plain_http[ModuleCtx.Conn_Name].conn
        conn = self.facade[ModuleCtx.Conn_Name]

        _ = conn.get('/my/path', params={'my-key': 'my-value'})

        expected_params = {'my-key': 'my-value', '_zato_path': '/my/path'}
        self.assertEqual(wrapper.calls, [('get', (ModuleCtx.CID,), {'params': expected_params})])

# ################################################################################################################################
# ################################################################################################################################

class RESTFacadeNamePrefixTestCase(TestCase):

    def setUp(self) -> 'None':
        self.out_plain_http = get_out_plain_http()
        self.facade = _PrefixedRESTFacade()
        self.facade.init(ModuleCtx.CID, self.out_plain_http)

# ################################################################################################################################

    def test_getitem_applies_prefix(self) -> 'None':

        conn = self.facade['Payments']

        self.assertIs(conn.conn, self.out_plain_http[ModuleCtx.Conn_Name_Prefixed].conn)

# ################################################################################################################################

    def test_getattr_applies_prefix(self) -> 'None':

        conn = self.facade.Payments

        self.assertIs(conn.conn, self.out_plain_http[ModuleCtx.Conn_Name_Prefixed].conn)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.util.api import import_module_from_path
from zato.common.util.exception import explain_exception

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

# ################################################################################################################################
# ################################################################################################################################

_cid = 'a1b2c3d4e5'

# The example module is imported the way a server imports a service from pickup, so its module name is its file stem.
_example_dir  = os.path.dirname(__file__)
_example_path = os.path.join(_example_dir, 'example.py')
_example      = import_module_from_path(_example_path)

ExampleService = _example.module.ExampleService

# ################################################################################################################################
# ################################################################################################################################

def _explain(handler:'callable_') -> 'str':
    try:
        handler()
    except Exception as e:
        out = explain_exception(e, _cid)
    else:
        raise Exception('The handler did not raise any exception')

    return out

# ################################################################################################################################

def _first_line(text:'str') -> 'str':
    lines = text.splitlines()
    out = lines[0]

    return out

# ################################################################################################################################

def _line_number_of(source_line:'str') -> 'int':
    with open(_example_path) as example_file:
        lines = example_file.readlines()

    for line_number, line in enumerate(lines, 1):
        if line.strip() == source_line:
            out = line_number
            break

    # .. the example module does not contain the line the test is looking for.
    else:
        raise Exception(f'Line `{source_line}` not found in `{_example_path}`')

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestExplainException:

    def test_missing_config_key(self) -> 'None':
        service = ExampleService()
        out = _explain(service.handle_missing_config_key)

        source_line = 'source = self.config.billing.source'
        line_number = _line_number_of(source_line)

        expected = '\n'.join([
            'AttributeError: no such key `billing`, existing keys: `demo`, `smtp`',
            '',
            f'{_example_path}, line {line_number}, in handle_missing_config_key',
            f'    {source_line}',
            '',
            f'CID: {_cid}',
        ])

        assert out == expected
        assert 'bunch.py' not in out
        assert 'Traceback' not in out

# ################################################################################################################################

    def test_missing_key_in_empty_config(self) -> 'None':
        service = ExampleService()
        out = _explain(service.handle_missing_key_in_empty_config)

        assert _first_line(out) == 'AttributeError: no such key `billing`, it has no keys'

# ################################################################################################################################

    def test_missing_connection(self) -> 'None':
        service = ExampleService()
        out = _explain(service.handle_missing_connection)

        assert _first_line(out) == 'KeyError: No such connection `crm`'

# ################################################################################################################################

    def test_inactive_connection(self) -> 'None':
        service = ExampleService()
        out = _explain(service.handle_inactive_connection)

        assert _first_line(out) == 'Inactive: `crm` is inactive'

# ################################################################################################################################

    def test_generic_error(self) -> 'None':
        service = ExampleService()
        out = _explain(service.handle_generic_error)

        assert _first_line(out) == 'Exception: Test error message'

# ################################################################################################################################

    def test_error_without_message(self) -> 'None':
        service = ExampleService()
        out = _explain(service.handle_error_without_message)

        assert _first_line(out) == 'Exception'

# ################################################################################################################################

    def test_error_with_cause(self) -> 'None':
        service = ExampleService()
        out = _explain(service.handle_error_with_cause)

        lines = out.splitlines()
        assert lines[0] == 'Exception: Customer lookup failed'
        assert lines[1] == 'Caused by KeyError: No such connection `crm`'
        assert lines[2] == ''
        assert lines[3].endswith(', in handle_error_with_cause')

# ################################################################################################################################

    def test_error_without_traceback(self) -> 'None':
        out = explain_exception(Exception('Test error message'), _cid)

        assert out == f'Exception: Test error message\n\nCID: {_cid}'

# ################################################################################################################################
# ################################################################################################################################

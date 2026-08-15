# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http.client import OK
from tempfile import TemporaryDirectory
from unittest import main, TestCase

# Zato
from zato.common.json_internal import dumps
from zato.common.skills.api import skill_file_name, skills_directory_name
from zato.common.test import _test_sec_def_id
from zato.common.typing_ import cast_
from zato.common.util.safeguards.config import build_safeguard_config
from zato.common.util.truncate.tokens import build_token_cap_config
from zato.server.connection.mcp.common import _message_prompt_not_found, InvalidCursor
from zato.server.connection.mcp.handler import MCPHandler, _error_invalid_params, _mcp_protocol_version
from zato.server.connection.mcp.prompts import SkillPrompts, _default_page_size
from zato.server.connection.mcp.session import MCPSessionManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone
    from zato.server.connection.mcp.registry import ToolRegistry

    ToolRegistry = ToolRegistry

# ################################################################################################################################
# ################################################################################################################################

_skill_template = """---
name: {name}
description: Description of {name}
---

# {name}

Instructions of {name}.
"""

# The file mode that takes all permissions away from a skill file
# and the one that makes it deletable again
_no_access_mode = 0
_full_access_mode = 0o644

# ################################################################################################################################
# ################################################################################################################################

def _write_skill(repo_location:'str', name:'str') -> 'None':
    """ Puts one skill on disk the way the Skills screen lays it out.
    """
    skill_directory = os.path.join(repo_location, skills_directory_name, name)
    os.makedirs(skill_directory)

    skill_path = os.path.join(skill_directory, skill_file_name)

    with open(skill_path, 'w') as skill_file:
        _ = skill_file.write(_skill_template.format(name=name))

# ################################################################################################################################
# ################################################################################################################################

class _MockToolRegistry:
    """ Mock tool registry with no tools - these tests are about prompts.
    """
    def get_tools_page(self, cursor:'any_'=None) -> 'tuple':
        return [], None

    def is_tool_allowed(self, service_name:'str') -> 'bool':
        return False

# ################################################################################################################################
# ################################################################################################################################

def _invoke_noop(service_name:'str', payload:'anydict') -> 'anydict':
    return {}

# ################################################################################################################################

def _make_handler(skill_prompts:'SkillPrompts') -> 'MCPHandler':
    """ Creates an MCPHandler serving the given skill prompts.
    """
    session_manager = MCPSessionManager()

    # Response shaping and input validation stay off in these tests
    safeguard_config = build_safeguard_config({})
    token_cap_config = build_token_cap_config({})

    registry = cast_('ToolRegistry', _MockToolRegistry())

    out = MCPHandler(registry, _invoke_noop, session_manager, safeguard_config, token_cap_config, False, skill_prompts)
    return out

# ################################################################################################################################

def _make_session(handler:'MCPHandler') -> 'str':
    session_manager = handler.session_manager
    out = session_manager.create(_mcp_protocol_version, _test_sec_def_id)
    return out

# ################################################################################################################################

def _make_request(method:'str', params:'anydictnone'=None, request_id:'any_'=1) -> 'anydict':

    out = {
        'jsonrpc': '2.0',
        'method': method,
        'id': request_id,
    }

    if params is not None:
        out['params'] = params

    return out

# ################################################################################################################################

_initialize_params = {
    'protocolVersion': _mcp_protocol_version,
    'capabilities': {},
    'clientInfo': {'name': 'test', 'version': '1.0'},
}

# ################################################################################################################################
# ################################################################################################################################

class SkillPromptsListing(TestCase):

    def test_has_prompts_follows_the_allow_list(self) -> 'None':
        """ Whether the gateway serves prompts at all is decided by its allow list alone.
        """
        self.assertFalse(SkillPrompts('', []).has_prompts())
        self.assertTrue(SkillPrompts('', ['invoice-mapping']).has_prompts())

    def test_page_holds_names_and_descriptions(self) -> 'None':
        """ A page carries names and descriptions only - the instructions do not travel here.
        """
        with TemporaryDirectory() as repo_location:

            _write_skill(repo_location, 'invoice-mapping')
            _write_skill(repo_location, 'order-lookup')

            prompts = SkillPrompts(repo_location, ['invoice-mapping', 'order-lookup'])
            page, next_cursor = prompts.get_prompts_page()

            self.assertIsNone(next_cursor)
            self.assertEqual(page, [
                {'name': 'invoice-mapping', 'description': 'Description of invoice-mapping'},
                {'name': 'order-lookup', 'description': 'Description of order-lookup'},
            ])

    def test_only_allowed_skills_are_listed(self) -> 'None':
        """ A skill on disk but outside the allow list has no line in the listing.
        """
        with TemporaryDirectory() as repo_location:

            _write_skill(repo_location, 'invoice-mapping')
            _write_skill(repo_location, 'order-lookup')

            prompts = SkillPrompts(repo_location, ['order-lookup'])
            page, _ = prompts.get_prompts_page()

            self.assertEqual(len(page), 1)
            self.assertEqual(page[0]['name'], 'order-lookup')

    def test_missing_file_has_no_line(self) -> 'None':
        """ A skill on the allow list whose file is gone has no line in the listing.
        """
        with TemporaryDirectory() as repo_location:

            _write_skill(repo_location, 'invoice-mapping')

            prompts = SkillPrompts(repo_location, ['invoice-mapping', 'gone'])
            page, _ = prompts.get_prompts_page()

            self.assertEqual(len(page), 1)
            self.assertEqual(page[0]['name'], 'invoice-mapping')

    def test_unreadable_file_has_no_line_and_others_keep_serving(self) -> 'None':
        """ A skill file without read permissions has no line in the listing
        and the readable skills keep serving.
        """
        with TemporaryDirectory() as repo_location:

            _write_skill(repo_location, 'invoice-mapping')
            _write_skill(repo_location, 'order-lookup')

            unreadable_path = os.path.join(repo_location, skills_directory_name, 'order-lookup', skill_file_name)
            os.chmod(unreadable_path, _no_access_mode)

            try:
                prompts = SkillPrompts(repo_location, ['invoice-mapping', 'order-lookup'])
                page, _ = prompts.get_prompts_page()

                self.assertEqual(len(page), 1)
                self.assertEqual(page[0]['name'], 'invoice-mapping')
            finally:
                # The temporary directory can only be cleaned up once the file is deletable again
                os.chmod(unreadable_path, _full_access_mode)

    def test_pagination(self) -> 'None':
        """ A listing larger than one page produces a cursor and the next page picks up from it.
        """
        with TemporaryDirectory() as repo_location:

            skill_count = _default_page_size + 3
            names = []

            for index in range(skill_count):
                name = f'skill-{index:04d}'
                names.append(name)
                _write_skill(repo_location, name)

            prompts = SkillPrompts(repo_location, names)

            page1, cursor = prompts.get_prompts_page()
            self.assertEqual(len(page1), _default_page_size)
            self.assertIsNotNone(cursor)

            page2, cursor = prompts.get_prompts_page(cursor)
            self.assertEqual(len(page2), 3)
            self.assertIsNone(cursor)

    def test_invalid_cursor_is_rejected(self) -> 'None':
        """ A cursor that is not an integer raises InvalidCursor.
        """
        prompts = SkillPrompts('', ['invoice-mapping'])
        self.assertRaises(InvalidCursor, prompts.get_prompts_page, 'not-a-number')

# ################################################################################################################################
# ################################################################################################################################

class SkillPromptsGet(TestCase):

    def test_get_prompt_reads_from_disk(self) -> 'None':
        """ An allowed name resolves to its document, read from disk now.
        """
        with TemporaryDirectory() as repo_location:

            _write_skill(repo_location, 'invoice-mapping')

            prompts = SkillPrompts(repo_location, ['invoice-mapping'])
            document = prompts.get_prompt('invoice-mapping')

            assert document is not None
            self.assertIn('Instructions of invoice-mapping', document.instructions)

    def test_disallowed_name_is_none(self) -> 'None':
        """ A skill on disk but outside the allow list is never served.
        """
        with TemporaryDirectory() as repo_location:

            _write_skill(repo_location, 'invoice-mapping')

            prompts = SkillPrompts(repo_location, [])
            self.assertIsNone(prompts.get_prompt('invoice-mapping'))

# ################################################################################################################################
# ################################################################################################################################

class HandleInitializeCapabilities(TestCase):

    def test_prompts_capability_only_with_skills(self) -> 'None':
        """ Initialize advertises prompts only when the gateway's skill list is non-empty.
        """
        handler = _make_handler(SkillPrompts('', []))

        request = _make_request('initialize', params=_initialize_params)
        mcp_response = handler.handle_raw_request(dumps(request), _test_sec_def_id)

        capabilities = mcp_response.body['result']['capabilities']
        self.assertNotIn('prompts', capabilities)

        handler = _make_handler(SkillPrompts('', ['invoice-mapping']))

        mcp_response = handler.handle_raw_request(dumps(request), _test_sec_def_id)

        capabilities = mcp_response.body['result']['capabilities']
        self.assertEqual(capabilities['prompts'], {})

# ################################################################################################################################
# ################################################################################################################################

class HandlePromptsList(TestCase):

    def test_prompts_list(self) -> 'None':
        """ prompts/list answers with the allowed skills' names and descriptions.
        """
        with TemporaryDirectory() as repo_location:

            _write_skill(repo_location, 'invoice-mapping')

            handler = _make_handler(SkillPrompts(repo_location, ['invoice-mapping']))
            session_id = _make_session(handler)

            request = _make_request('prompts/list')
            mcp_response = handler.handle_raw_request(dumps(request), _test_sec_def_id, session_id=session_id)

            self.assertEqual(mcp_response.status_code, OK)

            result = mcp_response.body['result']
            self.assertEqual(result['prompts'], [
                {'name': 'invoice-mapping', 'description': 'Description of invoice-mapping'},
            ])
            self.assertNotIn('nextCursor', result)

    def test_prompts_list_empty(self) -> 'None':
        """ A gateway with no skills answers with an empty list.
        """
        handler = _make_handler(SkillPrompts('', []))
        session_id = _make_session(handler)

        request = _make_request('prompts/list')
        mcp_response = handler.handle_raw_request(dumps(request), _test_sec_def_id, session_id=session_id)

        result = mcp_response.body['result']
        self.assertEqual(result['prompts'], [])

# ################################################################################################################################
# ################################################################################################################################

class HandlePromptsGet(TestCase):

    def test_prompts_get_returns_the_mcp_prompt_shape(self) -> 'None':
        """ prompts/get answers with the description and the instructions as one user message.
        """
        with TemporaryDirectory() as repo_location:

            _write_skill(repo_location, 'invoice-mapping')

            handler = _make_handler(SkillPrompts(repo_location, ['invoice-mapping']))
            session_id = _make_session(handler)

            request = _make_request('prompts/get', params={'name': 'invoice-mapping'})
            mcp_response = handler.handle_raw_request(dumps(request), _test_sec_def_id, session_id=session_id)

            self.assertEqual(mcp_response.status_code, OK)

            result = mcp_response.body['result']
            self.assertEqual(result['description'], 'Description of invoice-mapping')

            messages = result['messages']
            self.assertEqual(len(messages), 1)

            message = messages[0]
            self.assertEqual(message['role'], 'user')

            content = message['content']
            self.assertEqual(content['type'], 'text')
            self.assertIn('Instructions of invoice-mapping', content['text'])

    def test_prompts_get_disallowed_name(self) -> 'None':
        """ A name outside the allow list answers with the invalid-params error.
        """
        with TemporaryDirectory() as repo_location:

            _write_skill(repo_location, 'invoice-mapping')

            handler = _make_handler(SkillPrompts(repo_location, []))
            session_id = _make_session(handler)

            request = _make_request('prompts/get', params={'name': 'invoice-mapping'})
            mcp_response = handler.handle_raw_request(dumps(request), _test_sec_def_id, session_id=session_id)

            error = mcp_response.body['error']
            self.assertEqual(error['code'], _error_invalid_params)

    def test_prompts_get_unreadable_file(self) -> 'None':
        """ A file that exists but cannot be read answers exactly the way an absent one does.
        """
        with TemporaryDirectory() as repo_location:

            _write_skill(repo_location, 'invoice-mapping')

            unreadable_path = os.path.join(repo_location, skills_directory_name, 'invoice-mapping', skill_file_name)
            os.chmod(unreadable_path, _no_access_mode)

            try:
                handler = _make_handler(SkillPrompts(repo_location, ['invoice-mapping']))
                session_id = _make_session(handler)

                request = _make_request('prompts/get', params={'name': 'invoice-mapping'})
                mcp_response = handler.handle_raw_request(dumps(request), _test_sec_def_id, session_id=session_id)

                error = mcp_response.body['error']
                self.assertEqual(error['code'], _error_invalid_params)
                self.assertEqual(error['message'], _message_prompt_not_found)
            finally:
                # The temporary directory can only be cleaned up once the file is deletable again
                os.chmod(unreadable_path, _full_access_mode)

    def test_prompts_get_missing_name(self) -> 'None':
        """ A request without a name answers with the invalid-params error.
        """
        handler = _make_handler(SkillPrompts('', ['invoice-mapping']))
        session_id = _make_session(handler)

        request = _make_request('prompts/get', params={})
        mcp_response = handler.handle_raw_request(dumps(request), _test_sec_def_id, session_id=session_id)

        error = mcp_response.body['error']
        self.assertEqual(error['code'], _error_invalid_params)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################

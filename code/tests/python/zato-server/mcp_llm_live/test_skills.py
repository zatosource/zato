# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
import _agent
import _constants
import _helpers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class TestSkillsAsPrompts:
    """ The skills assigned to a gateway are its prompts - advertised in initialize,
    listed by prompts/list and served whole by prompts/get.
    """

# ################################################################################################################################

    def test_prompts_capability_is_advertised_only_with_skills(self, zato_server:'anydict') -> 'None':

        # The skills gateway advertises the prompts capability ..
        skills_client = _helpers.make_client(zato_server, _constants.Path_Skills)
        response = _helpers.initialize_response(skills_client)

        capabilities = response.json()['result']['capabilities']
        assert 'prompts' in capabilities, capabilities

        # .. and a gateway without skills does not.
        main_client = _helpers.make_client(zato_server, _constants.Path_Main)
        response = _helpers.initialize_response(main_client)

        capabilities = response.json()['result']['capabilities']
        assert 'prompts' not in capabilities, capabilities

# ################################################################################################################################

    def test_prompts_list_names_exactly_the_assigned_skills(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Skills)
        session_id = _helpers.open_session(client)

        response = client.jsonrpc('prompts/list', session_id=session_id)
        prompts = response.json()['result']['prompts']

        prompt_names = []

        for prompt in prompts:
            prompt_names.append(prompt['name'])

        assert prompt_names == [_constants.Skill_House_Style], prompt_names

# ################################################################################################################################

    def test_prompts_get_returns_the_skill_content(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Skills)
        session_id = _helpers.open_session(client)

        params = {'name': _constants.Skill_House_Style}
        response = client.jsonrpc('prompts/get', params=params, session_id=session_id)

        result = response.json()['result']

        # The instructions travel as the one message of the prompt
        # and carry the marker phrase the skill mandates.
        message = result['messages'][0]
        instructions = message['content']['text']

        assert _constants.Skill_Marker in instructions, instructions

# ################################################################################################################################

    def test_unassigned_skills_stay_invisible(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Skills)
        session_id = _helpers.open_session(client)

        # The skill exists on disk but is assigned to no gateway, so it is not listed ..
        response = client.jsonrpc('prompts/list', session_id=session_id)
        prompts = response.json()['result']['prompts']

        prompt_names = []

        for prompt in prompts:
            prompt_names.append(prompt['name'])

        assert _constants.Skill_Unassigned not in prompt_names, prompt_names

        # .. and reading it directly is invalid params.
        params = {'name': _constants.Skill_Unassigned}
        response = client.jsonrpc('prompts/get', params=params, session_id=session_id)

        body = response.json()
        assert body['error']['code'] == _constants.Error_Invalid_Params, body

# ################################################################################################################################
# ################################################################################################################################

class TestSkillUseByLLM:
    """ Behavioral proof the skill is used - the same task produces the mandated format
    only when the skill's instructions are in the conversation.
    """

# ################################################################################################################################

    def test_the_skill_shapes_the_answer_only_when_present(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Skills)

        # The skill's instructions come off the gateway itself, the way a real host reads them
        session_id = _helpers.open_session(client)

        params = {'name': _constants.Skill_House_Style}
        response = client.jsonrpc('prompts/get', params=params, session_id=session_id)

        instructions = response.json()['result']['messages'][0]['content']['text']

        task = f'What is the name and city of customer {_constants.Customer_ID}? Use the tools.'

        # With the skill in the conversation, the answer carries the mandated marker ..
        with_skill = _agent.run_agent(client, task, system_text=instructions)
        assert _helpers.text_contains(with_skill.final_text, _constants.Skill_Marker), with_skill.final_text

        # .. and without it, the marker never appears - the model has no way to know it.
        without_skill = _agent.run_agent(client, task)
        assert not _helpers.text_contains(without_skill.final_text, _constants.Skill_Marker), without_skill.final_text

        # Both runs answered the actual question, so the difference is the format alone.
        assert _helpers.text_contains(with_skill.final_text, _constants.Customer_Name), with_skill.final_text
        assert _helpers.text_contains(without_skill.final_text, _constants.Customer_Name), without_skill.final_text

# ################################################################################################################################
# ################################################################################################################################

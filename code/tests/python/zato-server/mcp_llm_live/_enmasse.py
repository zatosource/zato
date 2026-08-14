# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import tempfile

# PyYAML
from yaml import safe_dump

# local
import _constants
import containers
import keycloak_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist, stranydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# Where the zato binary lives, resolved the same way the conftest resolves it
_zato_base = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin  = os.path.join(_zato_base, 'code', 'bin', 'zato')

# How long one enmasse import may take, in seconds
_enmasse_timeout = 120

# ################################################################################################################################
# ################################################################################################################################

def build_security_list() -> 'dictlist':
    """ The security definitions every import carries - basic auth, an API key,
    a static bearer token and a Keycloak-issued one.
    """

    keycloak_token_url = keycloak_.get_token_url()
    keycloak_issuer = keycloak_.get_issuer()

    out:'dictlist' = [
        {
            'name': _constants.Sec_Basic,
            'type': 'basic_auth',
            'username': _constants.Username_Basic,
            'password': _constants.Password_Basic,
        },
        {
            'name': _constants.Sec_Basic_B,
            'type': 'basic_auth',
            'username': _constants.Username_Basic_B,
            'password': _constants.Password_Basic_B,
        },
        {
            'name': _constants.Sec_Basic_Shared,
            'type': 'basic_auth',
            'username': _constants.Username_Basic_Shared,
            'password': _constants.Password_Basic_Shared,
        },
        {
            'name': _constants.Sec_APIKey,
            'type': 'apikey',
            'header': _constants.APIKey_Header,
            'password': _constants.APIKey_Value,
        },
        {
            'name': _constants.Sec_Bearer_Static,
            'type': 'bearer_token',
            'static_token': _constants.Bearer_Static_Token,
        },
        {
            'name': _constants.Sec_Bearer_Keycloak,
            'type': 'bearer_token',
            'username': keycloak_.Client_Accounting,
            'password': keycloak_.Secret_Accounting,
            'auth_endpoint': keycloak_token_url,
            'issuer': keycloak_issuer,
            'audience': keycloak_.Audience_Main,
            'claims': [f'{keycloak_.Claim_Department}={keycloak_.Department_Accounting}'],
        },
    ]

    return out

# ################################################################################################################################

def build_group_list(main_members:'strlist | None' = None, shared_a_members:'strlist | None' = None) -> 'dictlist':
    """ The security groups every import carries. The main group's members and the A side's
    members may be overridden, which is how the tests prove that removing a definition
    from a group takes effect live while other groups keep working.
    """

    if main_members is None:
        main_members = [
            _constants.Sec_Basic,
            _constants.Sec_APIKey,
            _constants.Sec_Bearer_Static,
            _constants.Sec_Bearer_Keycloak,
        ]

    # The shared definition sits in both A's and B's groups, and A's group additionally
    # holds a definition of its own that B's group knows nothing about.
    if shared_a_members is None:
        shared_a_members = [_constants.Sec_Basic_Shared, _constants.Sec_Basic]

    out:'dictlist' = [
        {'name': _constants.Group_Main,     'members': main_members},
        {'name': _constants.Group_Iso_A,    'members': [_constants.Sec_Basic]},
        {'name': _constants.Group_Iso_B,    'members': [_constants.Sec_Basic_B]},
        {'name': _constants.Group_Iso_C,    'members': [_constants.Sec_Bearer_Static]},
        {'name': _constants.Group_Shared_A, 'members': shared_a_members},
        {'name': _constants.Group_Shared_B, 'members': [_constants.Sec_Basic_Shared]},
    ]

    return out

# ################################################################################################################################

def _gateway(name:'str', url_path:'str', **options:'object') -> 'stranydict':
    """ One mcp_gateway YAML entry - the CRM services, the main group and an active audit log
    unless the options say otherwise.
    """

    out:'stranydict' = {
        'name': name,
        'is_active': True,
        'url_path': url_path,
        'services': list(_constants.Service_List_CRM),
        'security_groups': [_constants.Group_Main],
        'is_audit_log_active': True,
    }

    out.update(options)

    return out

# ################################################################################################################################

def build_gateway_list() -> 'dictlist':
    """ Every gateway of the suite, one per capability family, so the options of one family
    never bleed into another family's assertions.
    """

    out:'dictlist' = [

        # The plain gateway - tool discovery, security, protocol, sessions and audit completeness
        _gateway(_constants.Gateway_Main, _constants.Path_Main),

        # Input validation on
        _gateway(_constants.Gateway_Validate, _constants.Path_Validate,
            validate_input=True),

        # Skills served as prompts
        _gateway(_constants.Gateway_Skills, _constants.Path_Skills,
            skills=[_constants.Skill_House_Style]),

        # Response shaping - the cap in truncate and block modes, the activation threshold,
        # and the same cap under two characters-per-token ratios
        _gateway(_constants.Gateway_Shaping_Truncate, _constants.Path_Shaping_Truncate,
            max_response_size=_constants.Shaping_Cap_Tokens,
            size_cap_mode='truncate'),

        _gateway(_constants.Gateway_Shaping_Block, _constants.Path_Shaping_Block,
            max_response_size=_constants.Shaping_Cap_Tokens,
            size_cap_mode='block'),

        _gateway(_constants.Gateway_Shaping_Threshold, _constants.Path_Shaping_Threshold,
            max_response_size=_constants.Shaping_Cap_Tokens,
            size_cap_mode='truncate',
            min_size_threshold=_constants.Shaping_Threshold_Tokens),

        _gateway(_constants.Gateway_Shaping_Wide, _constants.Path_Shaping_Wide,
            max_response_size=_constants.Shaping_Cap_Tokens,
            size_cap_mode='truncate',
            characters_per_token=_constants.Shaping_Ratio_Wide),

        _gateway(_constants.Gateway_Shaping_Narrow, _constants.Path_Shaping_Narrow,
            max_response_size=_constants.Shaping_Cap_Tokens,
            size_cap_mode='truncate',
            characters_per_token=_constants.Shaping_Ratio_Narrow),

        # Compaction - nulls, whitespace and base64
        _gateway(_constants.Gateway_Compaction, _constants.Path_Compaction,
            safeguards_strip_nulls=True,
            safeguards_collapse_whitespace=True,
            safeguards_strip_base64=True),

        # PII removal - the international detectors with validation and stable tokens,
        # the same land with one detector excluded, and a land the record never matches
        _gateway(_constants.Gateway_PII, _constants.Path_PII,
            safeguards_pii_enabled=True,
            safeguards_pii_lands=[_constants.PII_Land_Main],
            safeguards_pii_validate=True,
            safeguards_pii_stable_tokens=True),

        _gateway(_constants.Gateway_PII_Exclude, _constants.Path_PII_Exclude,
            safeguards_pii_enabled=True,
            safeguards_pii_lands=[_constants.PII_Land_Main],
            safeguards_pii_exclude=[_constants.PII_Exclude_Detector],
            safeguards_pii_validate=True),

        _gateway(_constants.Gateway_PII_Other_Land, _constants.Path_PII_Other_Land,
            safeguards_pii_enabled=True,
            safeguards_pii_lands=[_constants.PII_Land_Other],
            safeguards_pii_validate=True),

        # Content safety - cleaning modes with a URL allow list, and markup in reject mode
        _gateway(_constants.Gateway_Safety, _constants.Path_Safety,
            safeguards_normalize_unicode=True,
            safeguards_sanitize_markup=True,
            safeguards_url_policy_enabled=True,
            safeguards_url_allow_list=[_constants.Safety_Allowed_Host],
            safeguards_url_mode='remove'),

        _gateway(_constants.Gateway_Safety_Reject, _constants.Path_Safety_Reject,
            safeguards_sanitize_markup=True,
            safeguards_markup_mode='reject'),

        # Client JSONata filters, with input validation on so unknown parameters are provable
        _gateway(_constants.Gateway_Filters, _constants.Path_Filters,
            allow_client_filters=True,
            validate_input=True),

        # The lifecycle gateway - its options are flipped by re-imports mid-suite
        _gateway(_constants.Gateway_Lifecycle, _constants.Path_Lifecycle,
            max_response_size=_constants.Shaping_Cap_Tokens,
            size_cap_mode='truncate'),

        # The hot-deploy gateway serves only the probe service whose schema changes mid-suite
        _gateway(_constants.Gateway_Hotdeploy, _constants.Path_Hotdeploy,
            services=[_constants.Service_Deploy_Probe]),

        # The isolation trio - A and B share the CRM services but differ in every option
        # and group, A additionally serves the probe service and a skill of its own,
        # B has its own skill, and C shares nothing with either
        _gateway(_constants.Gateway_Iso_A, _constants.Path_Iso_A,
            services=[*_constants.Service_List_CRM, _constants.Service_Deploy_Probe],
            security_groups=[_constants.Group_Shared_A],
            skills=[_constants.Skill_House_Style],
            safeguards_pii_enabled=True,
            safeguards_pii_lands=[_constants.PII_Land_Main],
            safeguards_pii_validate=True,
            safeguards_pii_stable_tokens=True),

        _gateway(_constants.Gateway_Iso_B, _constants.Path_Iso_B,
            security_groups=[_constants.Group_Shared_B],
            skills=[_constants.Skill_Iso_B]),

        _gateway(_constants.Gateway_Iso_C, _constants.Path_Iso_C,
            services=[_constants.Service_Order_Status],
            security_groups=[_constants.Group_Iso_C]),
    ]

    return out

# ################################################################################################################################

def build_suite_config(
    gateway_overrides:'anydict | None' = None,
    main_members:'strlist | None' = None,
    shared_a_members:'strlist | None' = None,
    ) -> 'stranydict':
    """ The whole enmasse document of the suite as a dict - security, groups, gateways
    and the self.llm outconn. Gateway overrides are merged in by gateway name, which is
    how the lifecycle tests flip one option and import again.
    """

    gateway_list = build_gateway_list()

    if gateway_overrides:
        for gateway in gateway_list:
            if overrides := gateway_overrides.get(gateway['name']):
                gateway.update(overrides)

    out:'stranydict' = {
        'security': build_security_list(),
        'groups': build_group_list(main_members, shared_a_members),
        'mcp_gateway': gateway_list,
        'llm': [
            {
                'name': _constants.LLM_Outconn_Name,
                'address': containers.Ollama_OpenAI_URL,
                'model': containers.Model_Name,
                'api_key': 'not-needed-for-ollama',
            },
        ],
    }

    return out

# ################################################################################################################################

def run_import(server_directory:'str', config:'stranydict') -> 'None':
    """ Writes the config out as YAML and runs one enmasse import against the live server.
    """

    yaml_text = safe_dump(config, default_flow_style=False, sort_keys=False)

    tmp_yaml = os.path.join(tempfile.gettempdir(), f'zato-mcp-llm-live-{os.getpid()}.yaml')

    try:
        with open(tmp_yaml, 'w') as yaml_file:
            _ = yaml_file.write(yaml_text)

        result = subprocess.run(
            [_zato_bin, 'enmasse', server_directory, '--verbose', '--import', '--input', tmp_yaml],
            capture_output=True, text=True, timeout=_enmasse_timeout,
        )

        if result.returncode != 0:
            raise Exception(
                f'enmasse --import failed (exit {result.returncode}):\nstdout: {result.stdout}\nstderr: {result.stderr}')

    finally:
        if os.path.isfile(tmp_yaml):
            os.unlink(tmp_yaml)

# ################################################################################################################################
# ################################################################################################################################

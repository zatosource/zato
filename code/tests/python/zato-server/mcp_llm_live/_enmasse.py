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

        # Input validation on - the report service is the one with an optional field
        _gateway(_constants.Gateway_Validate, _constants.Path_Validate,
            services=[*_constants.Service_List_CRM, _constants.Service_Report_Build],
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

        # PII removal - the international detectors with validation and stable replacements,
        # the same land with one detector excluded, and a land the record never matches
        _gateway(_constants.Gateway_PII, _constants.Path_PII,
            safeguards_pii_enabled=True,
            safeguards_pii_lands=[_constants.PII_Land_Main],
            safeguards_pii_validate=True,
            safeguards_pii_stable_replacements=True),

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
            safeguards_pii_stable_replacements=True),

        _gateway(_constants.Gateway_Iso_B, _constants.Path_Iso_B,
            security_groups=[_constants.Group_Shared_B],
            skills=[_constants.Skill_Iso_B]),

        _gateway(_constants.Gateway_Iso_C, _constants.Path_Iso_C,
            services=[_constants.Service_Order_Status],
            security_groups=[_constants.Group_Iso_C]),

        # The conduct gateway - the reference service and the two tools told apart only by their docstrings
        _gateway(_constants.Gateway_Conduct, _constants.Path_Conduct,
            services=[_constants.Service_Fact_Get, _constants.Service_Account_Lookup, _constants.Service_Account_Query]),

        # The identity gateway admits only the B definition, whose password changes mid-suite
        _gateway(_constants.Gateway_Identity, _constants.Path_Identity,
            services=[_constants.Service_Order_Status],
            security_groups=[_constants.Group_Iso_B]),

        # The session-cap gateway is filled to the per-identity cap, so no other test shares it
        _gateway(_constants.Gateway_Sessions, _constants.Path_Sessions,
            services=[_constants.Service_Order_Status]),

        # The TTL gateway expires idle sessions after seconds, not the default half hour
        _gateway(_constants.Gateway_TTL, _constants.Path_TTL,
            services=[_constants.Service_Order_Status],
            session_ttl=_constants.Session_TTL_Seconds),

        # The runtime gateway serves the slow echo and the order confirmation services
        _gateway(_constants.Gateway_Runtime, _constants.Path_Runtime,
            services=[_constants.Service_Echo_Slow, _constants.Service_Order_Confirm]),

        # The docstring gateway serves the probe whose docstring changes mid-suite
        # and the service that has no docstring at all
        _gateway(_constants.Gateway_Docstring, _constants.Path_Docstring,
            services=[_constants.Service_Docstring_Probe, _constants.Service_Blank_Probe]),

        # The pipeline gateway runs every stage at once - compaction, PII, safety, the cap and client filters
        _gateway(_constants.Gateway_Pipeline, _constants.Path_Pipeline,
            services=[*_constants.Service_List_CRM, _constants.Service_Customer_List],
            safeguards_strip_nulls=True,
            safeguards_collapse_whitespace=True,
            safeguards_strip_base64=True,
            safeguards_pii_enabled=True,
            safeguards_pii_lands=[_constants.PII_Land_Main],
            safeguards_pii_validate=True,
            safeguards_pii_stable_replacements=True,
            safeguards_normalize_unicode=True,
            safeguards_sanitize_markup=True,
            safeguards_url_policy_enabled=True,
            safeguards_url_allow_list=[_constants.Safety_Allowed_Host],
            safeguards_url_mode='remove',
            max_response_size=_constants.Pipeline_Cap_Tokens,
            size_cap_mode='truncate',
            allow_client_filters=True),

        # PII removal together with truncation, for the boundary of the cut
        _gateway(_constants.Gateway_PII_Truncate, _constants.Path_PII_Truncate,
            services=[_constants.Service_Customer_List],
            safeguards_pii_enabled=True,
            safeguards_pii_lands=[_constants.PII_Land_Main],
            safeguards_pii_validate=True,
            safeguards_pii_stable_replacements=True,
            max_response_size=_constants.Pipeline_Cap_Tokens,
            size_cap_mode='truncate'),

        # Markup rejection together with a blocking cap - one response can violate both
        _gateway(_constants.Gateway_Reject_Both, _constants.Path_Reject_Both,
            services=[_constants.Service_Customer_List],
            safeguards_sanitize_markup=True,
            safeguards_markup_mode='reject',
            max_response_size=_constants.Pipeline_Cap_Tokens,
            size_cap_mode='block'),

        # Compaction together with a cap - the cap measures the compacted response
        _gateway(_constants.Gateway_Compact_Cap, _constants.Path_Compact_Cap,
            services=[_constants.Service_Text_Pad],
            safeguards_collapse_whitespace=True,
            max_response_size=_constants.Pipeline_Cap_Tokens,
            size_cap_mode='truncate'),

        # The same cap as the threshold gateway, with a threshold low enough to cross
        _gateway(_constants.Gateway_Threshold_Low, _constants.Path_Threshold_Low,
            max_response_size=_constants.Shaping_Cap_Tokens,
            size_cap_mode='truncate',
            min_size_threshold=_constants.Threshold_Low_Tokens),

        # One compaction stage per gateway - each acts alone
        _gateway(_constants.Gateway_Nulls, _constants.Path_Nulls,
            safeguards_strip_nulls=True),

        _gateway(_constants.Gateway_Whitespace, _constants.Path_Whitespace,
            safeguards_collapse_whitespace=True),

        _gateway(_constants.Gateway_Base64, _constants.Path_Base64,
            safeguards_strip_base64=True),

        # PII in its remaining variants - two lands, a directly named
        # detector with no land, and validation off
        _gateway(_constants.Gateway_PII_Two_Lands, _constants.Path_PII_Two_Lands,
            safeguards_pii_enabled=True,
            safeguards_pii_lands=[_constants.PII_Land_Main, _constants.PII_Land_Japan],
            safeguards_pii_validate=True),

        _gateway(_constants.Gateway_PII_Detector, _constants.Path_PII_Detector,
            safeguards_pii_enabled=True,
            safeguards_pii_detectors=[_constants.PII_Named_Detector],
            safeguards_pii_validate=True),

        _gateway(_constants.Gateway_PII_No_Validate, _constants.Path_PII_No_Validate,
            safeguards_pii_enabled=True,
            safeguards_pii_lands=[_constants.PII_Land_Main],
            safeguards_pii_validate=False),

        # Secrets removal - credential-shaped values become stable tokens
        _gateway(_constants.Gateway_Secrets, _constants.Path_Secrets,
            safeguards_secrets_enabled=True),

        # Content safety in its remaining modes - unicode in reject mode
        # and the URL policy in its neutralize and reject modes
        _gateway(_constants.Gateway_Unicode_Reject, _constants.Path_Unicode_Reject,
            safeguards_normalize_unicode=True,
            safeguards_unicode_mode='reject'),

        _gateway(_constants.Gateway_URL_Neutralize, _constants.Path_URL_Neutralize,
            safeguards_url_policy_enabled=True,
            safeguards_url_allow_list=[_constants.Safety_Allowed_Host],
            safeguards_url_mode='neutralize'),

        _gateway(_constants.Gateway_URL_Reject, _constants.Path_URL_Reject,
            safeguards_url_policy_enabled=True,
            safeguards_url_allow_list=[_constants.Safety_Allowed_Host],
            safeguards_url_mode='reject'),

        # The one gateway whose audit log is off
        _gateway(_constants.Gateway_Audit_Off, _constants.Path_Audit_Off,
            is_audit_log_active=False),

        # The operations gateway - services whose conduct the gateway must contain,
        # with an invoke timeout short enough for the archive build to overrun
        _gateway(_constants.Gateway_Ops, _constants.Path_Ops,
            services=[
                _constants.Service_Archive_Build,
                _constants.Service_Badge_Render,
                _constants.Service_Tag_Collect,
                _constants.Service_Ack_Silent,
                _constants.Service_Order_Status,
            ],
            invoke_timeout=_constants.Invoke_Timeout_Seconds),
    ]

    return out

# ################################################################################################################################

def build_suite_config(
    gateway_overrides:'anydict | None' = None,
    main_members:'strlist | None' = None,
    shared_a_members:'strlist | None' = None,
    ) -> 'stranydict':
    """ The whole enmasse document of the suite as a dict - security, groups, gateways
    and the self.llm outconn. Gateway overrides are merged in by name,
    which is how the tests flip one option and import again.
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

def run_import_file(server_directory:'str', input_path:'str') -> 'None':
    """ Runs one enmasse import of the given YAML file against the live server.
    """

    result = subprocess.run(
        [_zato_bin, 'enmasse', server_directory, '--verbose', '--import', '--input', input_path],
        capture_output=True, text=True, timeout=_enmasse_timeout,
    )

    if result.returncode != 0:
        raise Exception(
            f'enmasse --import failed (exit {result.returncode}):\nstdout: {result.stdout}\nstderr: {result.stderr}')

# ################################################################################################################################

def run_import(server_directory:'str', config:'stranydict') -> 'None':
    """ Writes the config out as YAML and runs one enmasse import against the live server.
    """

    yaml_text = safe_dump(config, default_flow_style=False, sort_keys=False)

    tmp_yaml = os.path.join(tempfile.gettempdir(), f'zato-mcp-llm-live-{os.getpid()}.yaml')

    try:
        with open(tmp_yaml, 'w') as yaml_file:
            _ = yaml_file.write(yaml_text)

        run_import_file(server_directory, tmp_yaml)

    finally:
        if os.path.isfile(tmp_yaml):
            os.unlink(tmp_yaml)

# ################################################################################################################################

def run_export(server_directory:'str', output_path:'str', include_type:'str') -> 'None':
    """ Runs one enmasse export of the given object types against the live server.
    """

    result = subprocess.run(
        [_zato_bin, 'enmasse', server_directory, '--verbose', '--export',
            '--output', output_path, '--include-type', include_type],
        capture_output=True, text=True, timeout=_enmasse_timeout,
    )

    if result.returncode != 0:
        raise Exception(
            f'enmasse --export failed (exit {result.returncode}):\nstdout: {result.stdout}\nstderr: {result.stderr}')

# ################################################################################################################################
# ################################################################################################################################

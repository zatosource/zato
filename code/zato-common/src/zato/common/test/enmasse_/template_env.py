# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.test.private_key_jwt import Env_Var_Private_Key, generate_rsa_private_key_pem

# ################################################################################################################################
# ################################################################################################################################

# The environment variables that the secrets of the enmasse test templates are read from,
# apart from the private key, which is generated.
Template_Secret_Env_Variables = (
    'BasicAuth1',
    'BasicAuth2',
    'BasicAuth3',
    'ConfluenceAPIToken',
    'DiscordToken',
    'EnmasseApiKey1',
    'EnmasseApiKey2',
    'EnmasseBearerToken1',
    'Enmasse_LDAP_Password',
    'Enmasse_LLM_API_Key',
    'Enmasse_OData_Client_Secret',
    'Enmasse_OData_Secret',
    'Enmasse_SAP_Client_Secret',
    'Enmasse_SAP_Secret',
    'IMAPPassword',
    'JiraAPIToken',
    'Microsoft365SecretValue',
    'MicrosoftFabricClientSecret',
    'MicrosoftPowerAutomateClientSecret',
    'MicrosoftTeamsSecretValue',
    'OdooPassword',
    'SMTPPassword',
    'SQL_Password_1',
    'SQL_Password_2',
    'SQL_Password_4',
    'SalesforceConsumerSecret',
    'SalesforcePassword',
    'SlackToken',
)

# The prefix of the value of each secret.
Template_Secret_Value_Prefix = 'Enmasse-Test-Secret-'

# ################################################################################################################################
# ################################################################################################################################

def set_template_environment() -> 'None':
    """ Sets each environment variable that the enmasse test templates read a secret from, unless it is set already,
    so that every import of a template, in the test process, in the enmasse CLI and in the servers that the tests start,
    resolves its secrets.
    """
    for name in Template_Secret_Env_Variables:
        if name not in os.environ:
            os.environ[name] = Template_Secret_Value_Prefix + name

    if Env_Var_Private_Key not in os.environ:
        os.environ[Env_Var_Private_Key] = generate_rsa_private_key_pem()

# ################################################################################################################################
# ################################################################################################################################

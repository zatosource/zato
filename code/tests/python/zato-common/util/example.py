# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.exception import Inactive
from zato.common.ext.bunch import Bunch
from zato.common.user_config import UserConfig, UserConfigFile

# ################################################################################################################################
# ################################################################################################################################

User_Config_Dir = '/opt/zato/env/qs-1/server1/config/repo/user-conf'

# ################################################################################################################################
# ################################################################################################################################

class ExampleService:
    """ Stands in for a user's service whose handle methods fail the way services do.
    """

    def __init__(self) -> 'None':
        self.config = Bunch()
        self.config.demo = Bunch()
        self.config.smtp = Bunch()
        self.empty_config = Bunch()

        self.user_config = UserConfig()
        self.user_config.zato_dir_names.append(User_Config_Dir)
        self.user_config.user = UserConfigFile('user.ini', self.user_config, {
            'demo': {},
            'smtp': {'host': 'smtp.example.com', 'port': 587},
        })

        self.empty_user_config = UserConfig()
        self.empty_user_config.zato_dir_names.append(User_Config_Dir)

# ################################################################################################################################

    def handle_missing_config_key(self) -> 'str':
        source = self.config.billing.source
        return source

# ################################################################################################################################

    def handle_missing_key_in_empty_config(self) -> 'str':
        source = self.empty_config.billing.source
        return source

# ################################################################################################################################

    def handle_missing_user_config_file(self) -> 'str':
        source = self.user_config.billing.source
        return source

# ################################################################################################################################

    def handle_missing_user_config_file_in_empty_store(self) -> 'str':
        source = self.empty_user_config.billing.source
        return source

# ################################################################################################################################

    def handle_missing_user_config_section(self) -> 'str':
        source = self.user_config.user.billing.source
        return source

# ################################################################################################################################

    def handle_missing_user_config_option(self) -> 'str':
        source = self.user_config.user.smtp.source
        return source

# ################################################################################################################################

    def handle_missing_connection(self) -> 'None':
        raise KeyError('No such connection `crm`')

# ################################################################################################################################

    def handle_inactive_connection(self) -> 'None':
        raise Inactive('crm')

# ################################################################################################################################

    def handle_generic_error(self) -> 'None':
        raise Exception('Test error message')

# ################################################################################################################################

    def handle_error_without_message(self) -> 'None':
        raise Exception()

# ################################################################################################################################

    def handle_error_with_cause(self) -> 'None':
        try:
            raise KeyError('No such connection `crm`')
        except KeyError as e:
            raise Exception('Customer lookup failed') from e

# ################################################################################################################################
# ################################################################################################################################

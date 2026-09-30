# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
from logging import getLogger

# Zato
from zato.admin.web.env_repo_local import handle_request as handle_request_locally
from zato.admin.web.views import method_allowed
from zato.admin.web.views.settings.base import SettingsBaseView
from zato.admin.web.views.settings.config import env_repo_page_config
from zato.admin.web.views.settings.utils import json_response
from zato.common.env_repo import Env_Repo, get_link_dir, get_new_repo_url, is_host_mode, parse_repo_name, read_current, \
    read_public_key, read_status, set_local_dir, write_request
from zato.common.util.updates import Updater, UpdaterConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest, HttpResponse, QueryDict
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

current_dir = os.path.dirname(os.path.abspath(__file__))

updater_config = UpdaterConfig(current_dir=current_dir)
updater = Updater(updater_config)

_Branch_Pattern = re.compile(r'^[A-Za-z0-9_./-]+$')

# ################################################################################################################################
# ################################################################################################################################

def _get_param(query:'QueryDict', name:'str') -> 'str':

    value = query.get(name, '')

    out = str(value).strip()
    return out

# ################################################################################################################################

def _set_local_dir() -> 'None':
    """ Points the link directory at a directory under the dashboard's base directory.
    """
    # config_dir is set at startup, after this module is imported.
    from zato.admin import settings as admin_settings

    path = os.path.join(admin_settings.config_dir, Env_Repo.Local_Dir_Name)
    set_local_dir(path)

# ################################################################################################################################
# ################################################################################################################################

class EnvRepoView(SettingsBaseView):

    def __init__(self) -> 'None':
        super().__init__(env_repo_page_config, updater, 'zato/env-repo/index.html')

# ################################################################################################################################

    def get_index_context(self) -> 'anydict':

        _set_local_dir()

        current = read_current() or {}
        current_repo = parse_repo_name(current.get('url', ''))

        context = super().get_index_context()
        context['public_key'] = read_public_key()
        context['new_repo_url'] = get_new_repo_url()
        context['new_repo_name'] = Env_Repo.New_Repo_Name
        context['current_branch'] = current.get('branch', '')

        # The address is shown the way a browser shows it.
        if current_repo:
            context['current_full_name'] = current_repo.full_name
            context['current_url'] = current_repo.https_url
        else:
            context['current_full_name'] = ''
            context['current_url'] = ''

        return context

# ################################################################################################################################

    @method_allowed('GET')
    def get_status(self, req:'HttpRequest') -> 'HttpResponse':

        _set_local_dir()

        data = {
            'status':  read_status(),
            'current': read_current(),
        }

        return json_response(data)

# ################################################################################################################################

    def _handle_request(self, req:'HttpRequest', action:'str') -> 'HttpResponse':
        """ Writes the request for the host if there is one, otherwise handles it in this process.
        """
        _set_local_dir()

        repo = parse_repo_name(_get_param(req.POST, 'url'))
        branch = _get_param(req.POST, 'branch')

        if not repo:
            return json_response({'error': 'Repository address must look like https://github.com/owner/name'}, success=False)

        if action == Env_Repo.Action_Switch and not _Branch_Pattern.match(branch):
            return json_response({'error': 'Branch name is not valid'}, success=False)

        try:
            if is_host_mode():
                write_request(action, repo.ssh_url, branch)
            else:
                handle_request_locally(action, repo.ssh_url, branch)
        except OSError as exception:
            logger.warning('Request not written to %s: %s', get_link_dir(), exception)
            return json_response({'error': f'Request could not be written: {exception}'}, success=False)

        data = {
            'full_name': repo.full_name,
            'url':       repo.ssh_url,
            'https_url': repo.https_url,
        }

        return json_response(data)

# ################################################################################################################################

    @method_allowed('POST')
    def check(self, req:'HttpRequest') -> 'HttpResponse':
        return self._handle_request(req, Env_Repo.Action_Check)

# ################################################################################################################################

    @method_allowed('POST')
    def switch(self, req:'HttpRequest') -> 'HttpResponse':
        return self._handle_request(req, Env_Repo.Action_Switch)

# ################################################################################################################################
# ################################################################################################################################

env_repo_view = EnvRepoView()

# ################################################################################################################################
# ################################################################################################################################

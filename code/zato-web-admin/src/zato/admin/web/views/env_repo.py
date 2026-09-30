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
from zato.admin.web.views import method_allowed
from zato.admin.web.views.settings.base import SettingsBaseView
from zato.admin.web.views.settings.config import env_repo_page_config
from zato.admin.web.views.settings.utils import json_response
from zato.common.env_repo import Env_Repo, get_deploy_key_url, get_new_repo_url, get_repo_ssh_url, is_available, \
    read_current, read_public_key, read_status, write_request
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

# The same shape that the host accepts, so a mistake is caught before the request leaves the container.
_URL_Pattern = re.compile(r'^git@github\.com:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git$')
_Login_Pattern = re.compile(r'^[A-Za-z0-9-]+$')
_Branch_Pattern = re.compile(r'^[A-Za-z0-9_./-]+$')

# ################################################################################################################################
# ################################################################################################################################

def _get_param(query:'QueryDict', name:'str') -> 'str':

    value = query.get(name, '')

    out = str(value).strip()
    return out

# ################################################################################################################################
# ################################################################################################################################

class EnvRepoView(SettingsBaseView):

    def __init__(self) -> 'None':
        super().__init__(env_repo_page_config, updater, 'zato/env-repo/index.html')

# ################################################################################################################################

    def get_index_context(self) -> 'anydict':

        current = read_current() or {}

        context = super().get_index_context()
        context['is_available'] = is_available()
        context['public_key'] = read_public_key()
        context['current_url'] = current.get('url', '')
        context['current_branch'] = current.get('branch', '')
        context['current_commit'] = current.get('commit', '')[:12]
        context['current_env_name'] = current.get('env_name', '')
        context['new_repo_name'] = Env_Repo.New_Repo_Name

        return context

# ################################################################################################################################

    @method_allowed('GET')
    def get_status(self, req:'HttpRequest') -> 'HttpResponse':

        data = {
            'status':  read_status(),
            'current': read_current(),
        }

        return json_response(data)

# ################################################################################################################################

    @method_allowed('GET')
    def get_links(self, req:'HttpRequest') -> 'HttpResponse':
        """ Returns the GitHub pages that create a repository from the template and add the deploy key to it.
        """
        login = _get_param(req.GET, 'login')

        if not _Login_Pattern.match(login):
            return json_response({'error': 'GitHub login must be letters, digits and dashes'}, success=False)

        data = {
            'new_repo_url':   get_new_repo_url(login),
            'deploy_key_url': get_deploy_key_url(login),
            'repo_ssh_url':   get_repo_ssh_url(login),
        }

        return json_response(data)

# ################################################################################################################################

    def _write_request(self, req:'HttpRequest', action:'str') -> 'HttpResponse':

        url = _get_param(req.POST, 'url')
        branch = _get_param(req.POST, 'branch')

        if not _URL_Pattern.match(url):
            return json_response({'error': 'Repository address must look like git@github.com:owner/name.git'}, success=False)

        if not _Branch_Pattern.match(branch):
            return json_response({'error': 'Branch name is not valid'}, success=False)

        try:
            write_request(action, url, branch)
        except OSError as exception:
            logger.warning('Request not written to %s: %s', Env_Repo.Link_Dir, exception)
            return json_response({'error': f'Request could not be written: {exception}'}, success=False)

        return json_response({})

# ################################################################################################################################

    @method_allowed('POST')
    def check(self, req:'HttpRequest') -> 'HttpResponse':
        return self._write_request(req, Env_Repo.Action_Check)

# ################################################################################################################################

    @method_allowed('POST')
    def switch(self, req:'HttpRequest') -> 'HttpResponse':
        return self._write_request(req, Env_Repo.Action_Switch)

# ################################################################################################################################
# ################################################################################################################################

env_repo_view = EnvRepoView()

# ################################################################################################################################
# ################################################################################################################################

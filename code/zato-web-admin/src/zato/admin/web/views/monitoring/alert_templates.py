# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import dumps
from logging import getLogger
from shutil import copytree

# Zato
from zato.admin.web.util import get_server_directory
from zato.admin.web.views import method_allowed
from zato.admin.web.views.config_files import build_index_response, ContentInfo, Definition, handle_persist, to_directory
from zato.common.alerting.rendering import get_default_template_dir, Template_Dir_Name
from zato.common.util.open_ import open_r

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpResponse
    from django.template.response import TemplateResponse
    from zato.common.typing_ import any_, anydict, anylist, strlist

    anydict = anydict
    anylist = anylist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_template_name = 'zato/monitoring/alert_templates.html'

# The one kind of file on this screen
Kind_Template = 'template'

# What a notification template's file name ends with
Template_Suffix = '.j2'

# The Jinja markers a template's contents are counted by
_block_marker = '{%'
_expression_marker = '{{'

# The shipped template a new one starts out as a copy of
_starter_template_name = 'email-body.j2'

# ################################################################################################################################
# ################################################################################################################################

def get_server_templates_directory() -> 'str':
    """ Where the server keeps its alert notification templates.
    """
    server_directory = get_server_directory()

    out = os.path.join(server_directory, 'config', 'repo', Template_Dir_Name)
    return out

# ################################################################################################################################

def ensure_directory(templates_directory:'str') -> 'None':
    """ A missing directory is seeded from the shipped defaults, an existing one is left alone.
    """
    if not os.path.exists(templates_directory):
        _ = copytree(get_default_template_dir(), templates_directory)
        logger.info('Alert templates: created %s', templates_directory)

# ################################################################################################################################
# ################################################################################################################################

class AlertTemplatesDefinition(Definition):
    """ The Alert templates screen on the kit - the notification templates under the server's
    alert-templates directory, one .j2 file each.
    """
    template_name = _template_name
    log_prefix = 'Alert templates'

    def __init__(self, templates_directory:'str') -> 'None':
        self.templates_directory = to_directory(templates_directory)

# ################################################################################################################################

    def get_directory_list(self) -> 'strlist':

        out = [self.templates_directory]
        return out

# ################################################################################################################################

    def get_extra_context(self) -> 'anydict':
        """ A new template starts out as the shipped email body.
        """
        starter_path = os.path.join(get_default_template_dir(), _starter_template_name)

        with open_r(starter_path) as starter_file:
            starter = starter_file.read()

        out = {'new_template_content_json': dumps(starter)}
        return out

# ################################################################################################################################

    def build_content_info(self, file_name:'str', content:'str') -> 'ContentInfo':
        """ A template is counted by its Jinja blocks and expressions.
        """
        out = ContentInfo(Kind_Template, content.count(_block_marker), content.count(_expression_marker))
        return out

# ################################################################################################################################

    def is_listed(self, name:'str') -> 'bool':
        """ Only .j2 files are templates, anything else in the directory is left out.
        """
        out = super().is_listed(name) and name.endswith(Template_Suffix)
        return out

# ################################################################################################################################

    def create(self, request_data:'anydict') -> 'anydict':

        if not request_data['file_name'].endswith(Template_Suffix):
            raise Exception(f'A template name must end with `{Template_Suffix}`')

        out = super().create(request_data)
        return out

# ################################################################################################################################

    def rename(self, request_data:'anydict') -> 'anydict':

        if not request_data['new_file_name'].endswith(Template_Suffix):
            raise Exception(f'A template name must end with `{Template_Suffix}`')

        out = super().rename(request_data)
        return out

# ################################################################################################################################
# ################################################################################################################################

def _get_definition() -> 'AlertTemplatesDefinition':
    """ The definition over the server's own directory - built per request because
    the server directory is read from the environment.
    """
    out = AlertTemplatesDefinition(get_server_templates_directory())
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':

    definition = _get_definition()
    ensure_directory(definition.templates_directory)

    out = build_index_response(req, definition)
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def persist(req:'any_') -> 'HttpResponse':

    out = handle_persist(req, _get_definition())
    return out

# ################################################################################################################################
# ################################################################################################################################

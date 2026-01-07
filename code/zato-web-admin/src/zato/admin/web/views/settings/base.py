# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from django.template.response import TemplateResponse

from zato.admin.web.views import method_allowed
from zato.admin.web.views.settings.handlers import RestartHandler

class SettingsBaseView:

    def __init__(self, page_config, updater, template_name):
        self.page_config = page_config
        self.updater = updater
        self.template_name = template_name
        self.restart_handler = RestartHandler(updater)

    def get_index_context(self):
        return {
            'page_config': self.page_config
        }

    @method_allowed('GET')
    def index(self, req):
        context = self.get_index_context()
        return TemplateResponse(req, self.template_name, context)

    @method_allowed('POST')
    def restart_scheduler(self, req):
        return self.restart_handler.restart_scheduler(req)

    @method_allowed('POST')
    def restart_server(self, req):
        return self.restart_handler.restart_server(req)

    @method_allowed('POST')
    def restart_proxy(self, req):
        return self.restart_handler.restart_proxy(req)

    @method_allowed('POST')
    def restart_dashboard(self, req):
        return self.restart_handler.restart_dashboard(req)

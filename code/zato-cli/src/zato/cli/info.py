# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.cli import ManageCommand
from zato.common.api import INFO_FORMAT

DEFAULT_COLS_WIDTH = '30,90'

class Info(ManageCommand):
    """ Shows detailed information regarding a chosen Zato component
    """
    # Changed in 2.0 - --json replaced with --format
    opts = [
        {'name':'--format', 'help':'Output format, must be one of text, json or yaml, default: {}'.format(INFO_FORMAT.TEXT),
           'default':INFO_FORMAT.TEXT},
        {'name':'--cols_width', 'help':'A list of columns width to use for the table output, default: {}'.format(DEFAULT_COLS_WIDTH)}
    ]

    def _on_server(self, args):

        # stdlib
        import os

        # yaml
        import yaml

        # Zato
        from zato.common.component_info import format_info, get_info

        class _Dumper(yaml.SafeDumper):
            def represent_none(self, data):
                return self.represent_scalar('tag:yaml.org,2002:null', '')

        os.chdir(self.original_dir)
        info = get_info(os.path.abspath(args.path), args.format)
        self.logger.info(format_info(info, args.format, args.cols_width if args.cols_width else DEFAULT_COLS_WIDTH, _Dumper))

    _on_scheduler = _on_lb = _on_web_admin = _on_server

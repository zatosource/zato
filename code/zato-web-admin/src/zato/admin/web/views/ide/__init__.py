# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from zato.admin.web.views.ide.complete import complete_python, goto_definition
from zato.admin.web.views.ide.explorer import list_directory
from zato.admin.web.views.ide.lint import lint_python
from zato.admin.web.views.ide.logs import stream_logs, get_log_history
from zato.admin.web.views.ide.terminal import terminal_create, terminal_write, terminal_resize, terminal_close, terminal_stream

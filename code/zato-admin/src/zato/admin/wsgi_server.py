# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
from wsgiref.simple_server import make_server

# Django
from django.core.handlers.wsgi import WSGIHandler
from django.core.management import call_command
from django.core.servers.basehttp import AdminMediaHandler

# Werkzeug
from werkzeug.debug import DebuggedApplication

def main(host, port, base_dir):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.admin.settings'
    call_command('syncdb', interactive=True)
    call_command('loaddata', os.path.join(base_dir, 'config', 'repo', 'initial-data.json'))

    app = WSGIHandler()
    app = DebuggedApplication(app, evalex=True)
    server = make_server(host, port, AdminMediaHandler(app))

    # TODO: Make the server actually listen on HTTPS instead of HTTP
    print("ZatoAdmin ready at https://{0}:{1}/".format(host, port))
    server.serve_forever()

if __name__ == '__main__':
    main()

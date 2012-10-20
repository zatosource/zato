# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

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
import sys

def _prepare_buildout(has_pymqi):
    buildout = open('./buildout.cfg.template').read()
    if has_pymqi:
        buildout = buildout.replace('#PYMQI_MARKER', '')
        
    open('./buildout.cfg', 'w').write(buildout)

if __name__ == '__main__':
    has_pymqi = len(sys.argv) and str(sys.argv[1]) == '0'
    _prepare_buildout(has_pymqi)


    

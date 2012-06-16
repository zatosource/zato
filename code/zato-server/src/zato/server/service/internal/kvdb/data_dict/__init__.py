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

# Zato Redis key layout

# TODO: Document it properly

# zato:kvdb:data-dict:system - a list of systems
# zato:kvdb:data-dict:dictionary - a dictionary of list of dictionaries for each of the systems
# zato:kvdb:data-dict:$SYSTEM_NAME:dictionary - a dictionary for each of the systems

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

# zato:kvdb:data-dict:item
# {
#  '1': 'ESB:::curreny::EUR',
#  '2': 'ESB:::currency:::JPY',
#  '3': 'ESB:::country_code:::CH',
#  '4': 'CRM:::CURRENCY:::978',
# }

# 'zato:kvdb:data-dict:translation:::ESB:::currency:::EUR:::CRM:::CURRENCY:::978':{'id':'1', 'item1':'1', 'item2':'4'}

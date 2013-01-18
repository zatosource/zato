#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at gefira.pl>

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
import logging, os

# lxml
from lxml import etree

include_prefix = '<!-- include'
include_suffix = ' -->'

logging.basicConfig()

def main():
    out = []
    template = open('./wsdl-template.xml')
    for line in template:
        if line.startswith(include_prefix):
            path = line.replace(include_prefix, '').replace(include_suffix, '').strip()
            path = os.path.abspath(path)
            
            try:
                include = open(path).read().rstrip() + '\n'
            except IOError, e:
                logging.error("Can't include file [{}], e:[{}]".format(path, e))
            else:
                out.append(include)
        else:
            out.append(line)
        
    out = ''.join(out)
    open('./zato.wsdl', 'w').write(out)
        
if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
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


    

# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import Formatter

# ################################################################################################################################
# ################################################################################################################################

# Based on http://stackoverflow.com/questions/384076/how-can-i-make-the-python-logging-output-to-be-colored
class ColorFormatter(Formatter):

    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
    RESET_SEQ = '\033[0m'
    COLOR_SEQ = '\033[1;%dm'
    BOLD_SEQ = '\033[1m'

    COLORS = {
      'WARNING': YELLOW,
      'INFO': WHITE,
      'DEBUG': BLUE,
      'CRITICAL': YELLOW,
      'ERROR': RED,
      'TRACE1': YELLOW
    }

    def __init__(self, fmt):
        self.use_color = True
        super(ColorFormatter, self).__init__(fmt)

# ################################################################################################################################

    def formatter_msg(self, msg, use_color=True):
        if use_color:
            msg = msg.replace('$RESET', self.RESET_SEQ).replace('$BOLD', self.BOLD_SEQ)
        else:
            msg = msg.replace('$RESET', '').replace('$BOLD', '')
        return msg

# ################################################################################################################################

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in self.COLORS:
            fore_color = 30 + self.COLORS[levelname]
            levelname_color = self.COLOR_SEQ % fore_color + levelname + self.RESET_SEQ
            record.levelname = levelname_color

        return Formatter.format(self, record)

# ################################################################################################################################
# ################################################################################################################################

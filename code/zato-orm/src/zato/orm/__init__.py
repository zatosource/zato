# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

class label:
    """ Each object has its name and all of them are kept here. They are either simple labels
    or patterns with placeholds to fill with actual data in run-time.
    """
    class group:
        """ Names of groups.
        """
        class conf:
            """ Configuration items.
            """
            process = 'zato.conf.process'

    class sub_group:
        """ Names of sub-groups.
        """
        class conf:
            """ Configuration items.
            """
            process_bst = 'zato.conf.process.bst'

    class item:
        """ Actual items such as configuration values or run-time instances.
        """
        process_bst_inst_current = 'zato.inst.process.bst.current.%s.%s' # def_tag.object_tag
        process_bst_inst_history = 'zato.inst.process.bst.history.%s.%s' # ditto

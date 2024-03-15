# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Brython
from browser import document as doc

# Zato
from zato.common.json_internal import loads

# ################################################################################################################################

class SelectChanger(object):
    """ Links two SELECT fields so that changing value in one re-populates the other with associated values.
    """
    def __init__(self, select_source, select_target, data_source='id_select_changer_source'):
        self.data_source = data_source
        self.select_source = doc[select_source]
        self.select_target = doc[select_target]
        self.data = None

    def run(self):
        self.data = loads(doc[self.data_source].text)
        self.select_source.bind('change', self.on_source_change)

    def on_source_change(self, e):
        value = e.srcElement.value
        value = self.data[value] if value else ''
        self.select_target.set_value(value)

# ################################################################################################################################

sc = SelectChanger('id_topic_name', 'id_hook_service_name')
sc.run()

# ################################################################################################################################

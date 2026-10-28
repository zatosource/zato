# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.portal.sample import section_alerts, section_cpas, section_messages, section_partners, \
    section_registrations, wizards
from zato.common.b2b.portal.sample.common import State_Tones

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strdictdict

# ################################################################################################################################
# ################################################################################################################################

def _build() -> 'strdictdict':

    alerts = section_alerts.build_alerts()
    rules = section_alerts.build_rules()
    partners = section_partners.build()
    registrations = section_registrations.build()
    cpas = section_cpas.build()
    messages = section_messages.build()

    rules['wizard'] = wizards.rule_wizard()
    partners['wizard'] = wizards.partner_wizard()
    registrations['wizard'] = wizards.registration_wizard()
    cpas['wizard'] = wizards.cpa_wizard()

    # A rule is enabled and disabled by a switch in its own row
    rules['toggle'] = {
        'label': 'Enabled',
        'on_state': 'Enabled',
        'on_tone': State_Tones['Enabled'],
        'off_state': 'Disabled',
        'off_tone': State_Tones['Disabled'],
    }

    out:'strdictdict' = {}

    for section in (alerts, rules, partners, registrations, cpas, messages):
        out[section['slug']] = section

    return out

# ################################################################################################################################

Sections = _build()

# ################################################################################################################################
# ################################################################################################################################

def _entry(label:'str', slug:'str') -> 'anydict':
    section = Sections[slug]
    out = {'label': label, 'slug': slug, 'href': section['path']}
    return out

# ################################################################################################################################

# The order of priority in production, which each user may change by dragging the entries
Navigation:'anylist' = [
    _entry('Message log', 'messages'),
    _entry('Alerts', 'alerts'),
    _entry('Trading partners', 'partners'),
    _entry('CPAs', 'cpas'),
    _entry('Registrations', 'registrations'),
    _entry('Alert rules', 'alert-rules'),
]

# ################################################################################################################################
# ################################################################################################################################

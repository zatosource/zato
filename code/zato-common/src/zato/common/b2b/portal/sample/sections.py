# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.portal.sample import section_agreements, section_alerts, section_messages, section_partners, wizards
from zato.common.b2b.portal.sample.common import State_Tones
from zato.common.b2b.portal.sample.parties import Partner_By_Key

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
    agreements = section_agreements.build()
    messages = section_messages.build()

    rules['wizard'] = wizards.rule_wizard()
    partners['wizard'] = wizards.partner_wizard()
    for partner_key, partner_agreements in agreements['scopes'].items():
        partner = Partner_By_Key[partner_key]
        partner_agreements['wizard'] = wizards.agreement_wizard(partner)

    # A rule is enabled and disabled by a switch in its own row
    rules['toggle'] = {
        'label': 'Enabled',
        'on_state': 'Enabled',
        'on_tone': State_Tones['Enabled'],
        'off_state': 'Disabled',
        'off_tone': State_Tones['Disabled'],
    }

    out:'strdictdict' = {}

    for section in (alerts, rules, partners, agreements, messages):
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
    _entry('Alerts', 'alerts'),
    _entry('Message log', 'messages'),
    _entry('Trading partners', 'partners'),
]

# ################################################################################################################################
# ################################################################################################################################

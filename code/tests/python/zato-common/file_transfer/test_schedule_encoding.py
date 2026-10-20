# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.file_transfer.api import Default_Encoding, Encoding
from zato.common.util.file_transfer_scheduler import apply_schedule_defaults, export_schedule_list, schedule_from_yaml

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

_schedule_id = 'schedule-encoding-1'

# ################################################################################################################################
# ################################################################################################################################

def _yaml_schedule(**extra:'str') -> 'stranydict':
    """ A schedule in the shape enmasse reads it in, with only the required fields unless the test adds more.
    """
    out:'stranydict' = {
        'name': 'invoices.hourly',
        'directory': '/incoming/invoices',
        'service': 'invoices.process',
        'run_every': 5,
        'run_unit': 'minutes',
    }
    out.update(extra)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_default_encoding_is_utf_8() -> 'None':
    assert Default_Encoding == Encoding.UTF_8

# ################################################################################################################################

def test_a_stored_schedule_without_an_encoding_reads_utf_8() -> 'None':

    schedule = _yaml_schedule()
    apply_schedule_defaults(schedule)

    assert schedule['encoding'] == Encoding.UTF_8

# ################################################################################################################################

def test_a_stored_encoding_is_kept() -> 'None':

    schedule = _yaml_schedule(encoding=Encoding.CP1253)
    apply_schedule_defaults(schedule)

    assert schedule['encoding'] == Encoding.CP1253

# ################################################################################################################################

def test_import_without_an_encoding_reads_utf_8() -> 'None':

    schedule = schedule_from_yaml(_yaml_schedule(), _schedule_id)

    assert schedule['encoding'] == Encoding.UTF_8

# ################################################################################################################################

def test_import_with_an_encoding() -> 'None':

    schedule = schedule_from_yaml(_yaml_schedule(encoding=Encoding.ISO_8859_8), _schedule_id)

    assert schedule['encoding'] == Encoding.ISO_8859_8

# ################################################################################################################################

def test_export_leaves_out_the_default_encoding() -> 'None':

    schedule = schedule_from_yaml(_yaml_schedule(), _schedule_id)
    exported = export_schedule_list([schedule])

    assert 'encoding' not in exported[0]

# ################################################################################################################################

def test_export_and_import_keep_an_encoding() -> 'None':

    schedule = schedule_from_yaml(_yaml_schedule(encoding=Encoding.CP1250), _schedule_id)
    exported = export_schedule_list([schedule])

    assert exported[0]['encoding'] == Encoding.CP1250

    imported = schedule_from_yaml(exported[0], _schedule_id)
    assert imported['encoding'] == Encoding.CP1250

# ################################################################################################################################
# ################################################################################################################################

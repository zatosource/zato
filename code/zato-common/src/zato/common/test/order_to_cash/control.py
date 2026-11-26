# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The control files through which the order-to-cash tests inject faults into the services of a test server,
# and the trail of the steps that the services complete. The control files are kept in the server directory,
# which the services and the tests reach under the same path.

# stdlib
import glob
import os
import time

# Zato
from zato.common.test.order_to_cash.models import Store
from zato.common.test.received_store import record

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class Fault:
    """ The points at which a service fails while the control files say so.
    """

    # Fulfillment and invoicing fail before they publish, as when the warehouse or the ERP is unavailable
    Fulfillment = 'fulfillment'
    Invoicing   = 'invoicing'

    # The intake fails after it published the accepted order
    Intake_After_Publish = 'intake-after-publish'

# ################################################################################################################################
# ################################################################################################################################

# The directory of the control files in the server directory
_control_dir_name = 'order-to-cash-control'

# The file with the time that each step takes, in seconds
_step_delay_file_name = 'step-delay'

# What separates the parts of the name of a failure file
_separator = '.'

# ################################################################################################################################
# ################################################################################################################################

def _get_control_dir(server_directory:'str') -> 'str':
    out = os.path.join(server_directory, _control_dir_name)
    return out

# ################################################################################################################################

def _get_failure_pattern(server_directory:'str', fault:'str', po_number:'str') -> 'str':
    control_dir = _get_control_dir(server_directory)

    out = os.path.join(control_dir, f'{fault}{_separator}{po_number}{_separator}*')
    return out

# ################################################################################################################################
# ################################################################################################################################

def fail_attempts(server_directory:'str', fault:'str', po_number:'str', count:'int') -> 'None':
    """ Makes the next attempts of a service for a purchase order fail at the fault point, as many of them as given.
    """
    control_dir = _get_control_dir(server_directory)
    os.makedirs(control_dir, exist_ok=True)

    for idx in range(count):
        path = os.path.join(control_dir, f'{fault}{_separator}{po_number}{_separator}{idx}')

        with open(path, 'w'):
            pass

# ################################################################################################################################

def set_step_delay(server_directory:'str', seconds:'float') -> 'None':
    """ Makes each step of each service take the given time, which keeps orders in flight while a test acts.
    """
    control_dir = _get_control_dir(server_directory)
    os.makedirs(control_dir, exist_ok=True)

    path = os.path.join(control_dir, _step_delay_file_name)

    with open(path, 'w') as delay_file:
        _ = delay_file.write(str(seconds))

# ################################################################################################################################

def clear_step_delay(server_directory:'str') -> 'None':
    path = os.path.join(_get_control_dir(server_directory), _step_delay_file_name)

    if os.path.exists(path):
        os.remove(path)

# ################################################################################################################################

def count_pending_failures(server_directory:'str', fault:'str', po_number:'str') -> 'int':
    """ Returns how many of the failures requested for a purchase order no attempt has claimed yet.
    """
    pattern = _get_failure_pattern(server_directory, fault, po_number)

    out = len(glob.glob(pattern))
    return out

# ################################################################################################################################
# ################################################################################################################################

def claim_failure(service:'Service', fault:'str', po_number:'str') -> 'bool':
    """ Claims one failure requested for a purchase order at the fault point. Each failure is claimed by one attempt only,
    as a file that only one attempt can remove.
    """
    pattern = _get_failure_pattern(service.server.base_dir, fault, po_number)

    for path in sorted(glob.glob(pattern)):
        try:
            os.remove(path)
        except FileNotFoundError:
            continue
        else:
            return True

    return False

# ################################################################################################################################

def wait_step_delay(service:'Service') -> 'None':
    """ Waits for the time that the control files give each step, if any.
    """
    path = os.path.join(_get_control_dir(service.server.base_dir), _step_delay_file_name)

    # Without the file the steps take no extra time
    if not os.path.exists(path):
        return

    with open(path) as delay_file:
        seconds = float(delay_file.read())

    time.sleep(seconds)

# ################################################################################################################################

def record_step(service:'Service', step:'str', po_number:'str', **details:'any_') -> 'None':
    """ Records in the trail that a service completed a step for a purchase order.
    """
    item = {
        'po_number': po_number,
        'step': step,
        'service': service.name,
        'cid': service.cid,
    }
    item.update(details)

    record(service, Store.Trail, item)

# ################################################################################################################################
# ################################################################################################################################

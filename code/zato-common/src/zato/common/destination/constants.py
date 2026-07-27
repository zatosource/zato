# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The vocabulary a channel's destination list is written in. The type ids and the option
# names are the ones the Dashboard writes into a channel's configuration, so they are the
# same strings end to end - from the form, through storage, to the dispatcher that resolves
# the connection a destination names.

# ################################################################################################################################
# ################################################################################################################################

class DestinationType:
    """ The kinds of outgoing connection a destination points at.
    """
    REST = 'rest'
    MLLP = 'hl7-mllp'
    FHIR = 'hl7-fhir'
    SMTP = 'smtp'

# ################################################################################################################################

class DeliveryMode:
    """ How the destinations of one channel receive a message - all of them at once,
    or one after another in the order they were declared in. The third mode is the
    service making the calls itself and is not available yet.
    """
    Same_Time       = 'same-time'
    In_Order        = 'in-order'
    Service_Decides = 'service-decides'

# ################################################################################################################################

class DestinationOption:
    """ The per-type options a destination carries alongside the connection it names.
    """
    Method  = 'method'
    Path    = 'path'
    To      = 'to'
    Subject = 'subject'

# ################################################################################################################################
# ################################################################################################################################

# Every type a destination may be of
Known_Destination_Types = (
    DestinationType.REST,
    DestinationType.MLLP,
    DestinationType.FHIR,
    DestinationType.SMTP,
)

# The delivery modes a channel may actually be configured with
Active_Delivery_Modes = (
    DeliveryMode.Same_Time,
    DeliveryMode.In_Order,
)

# ################################################################################################################################
# ################################################################################################################################

# What a channel's respond-from setting holds when the service produces the caller's reply
Respond_From_Service = 'service'

# The mode a channel delivers in when its configuration does not name one
Default_Delivery_Mode = DeliveryMode.Same_Time

# Whether a destination receives messages when its configuration does not say
Default_Is_Active = True

# ################################################################################################################################
# ################################################################################################################################

# How many further attempts one hop gets after its first one failed, and how long to wait between them
Default_Retry_Count = 2
Default_Retry_Sleep_Seconds = 1.0

# ################################################################################################################################
# ################################################################################################################################

# The HTTP method a REST or FHIR destination uses when its options do not name one
Default_Method = 'POST'

# The path a FHIR destination posts to when its options do not name one
Default_Path = ''

# The recipient and the subject line an email destination uses when its options do not name them
Default_To = ''
Default_Subject = ''

# ################################################################################################################################
# ################################################################################################################################

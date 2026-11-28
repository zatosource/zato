# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.xml_.message import from_plain_dict as _from_plain_dict, parse as _parse, XMLMessage

# Re-exported for callers that import them from here.
from zato.common.util.xml_.message import bytes_by_content_id as bytes_by_content_id  # noqa: F401
from zato.common.util.xml_.message import serialize as serialize                      # noqa: F401
from zato.common.util.xml_.message import to_lexical as to_lexical                    # noqa: F401
from zato.common.util.xml_.message import to_plain_dict as to_plain_dict              # noqa: F401

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict
    any_ = any_
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

class SOAPMessage(XMLMessage):
    """ A SOAP message - an XMLMessage specialized only by name. Every SOAP-family
    builder and parser produces and consumes these, and faults surface as the one
    SOAPFault exception.
    """

# ################################################################################################################################
# ################################################################################################################################

def parse(source:'any_', parts:'bytes_by_content_id | None'=None) -> 'SOAPMessage':
    """ Parses XML into a SOAPMessage - the generic parser with our node type.
    """
    out = _parse(source, parts, message_class=SOAPMessage)
    return out

# ################################################################################################################################

def from_plain_dict(data:'anydict') -> 'SOAPMessage':
    """ Builds a SOAPMessage of a plain dict - the generic builder with our node type.
    """
    out = _from_plain_dict(data, message_class=SOAPMessage)
    return out

# ################################################################################################################################
# ################################################################################################################################

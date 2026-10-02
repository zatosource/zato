# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.common.audit_log.common import AuditEvent, AuditOutcome, AuditSource
from zato.common.hl7.ccda.convert import convert
from zato.common.hl7.ccda.exception import CCDAError
from zato.common.hl7.ccda.paths import get_converter_dir, is_converter_installed
from zato.server.commands import CommandsFacade

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strbytes, strdict
    from zato.fhir.r4_0_1.resources import Bundle
    from zato.server.base.parallel import ParallelServer

    strbytes = strbytes
    strdict  = strdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class CCDAFacade:
    """ Converts C-CDA documents to FHIR bundles from services via self.ccda, and from channels that convert on arrival.
    """
    cid: 'str'
    object_name: 'str'
    server: 'ParallelServer'
    commands: 'CommandsFacade'

    def init(self, cid:'str', server:'ParallelServer', object_name:'str') -> 'None':
        self.cid = cid
        self.server = server
        self.object_name = object_name
        self.commands = CommandsFacade()
        self.commands.init(server)

# ################################################################################################################################

    def to_fhir(self, document:'strbytes') -> 'Bundle':
        """ Converts one document and returns the bundle it became - the conversion is audited either way.
        """
        try:
            result = convert(document, commands=self.commands, cid=self.cid)

        except CCDAError as e:
            self._audit(AuditOutcome.Error, data=e.msg, attrs={'reason': e.reason, 'stderr': e.stderr})
            raise

        else:
            attrs = {
                'root_template': result.root_template,
                'resource_count': str(result.resource_count),
                'document_size': str(result.document_size),
            }
            self._audit(AuditOutcome.OK, duration_ms=result.duration_ms, attrs=attrs)

            out = result.bundle
            return out

# ################################################################################################################################

    def _audit(self, outcome:'str', *, duration_ms:'int'=0, data:'str'='', attrs:'strdict') -> 'None':
        _ = self.server.service_audit_log.insert(
            AuditSource.CCDA,
            AuditEvent.Note,
            self.object_name,
            cid=self.cid,
            outcome=outcome,
            duration_ms=duration_ms,
            data=data,
            attrs=attrs,
        )

# ################################################################################################################################
# ################################################################################################################################

def log_converter_status() -> 'None':
    """ Says at startup whether the converter is in place and where it was looked for.
    """
    converter_dir = get_converter_dir()

    if is_converter_installed():
        logger.info('FHIR converter found in `%s`', converter_dir)
    else:
        logger.info('FHIR converter not found in `%s`, C-CDA documents cannot be converted', converter_dir)

# ################################################################################################################################
# ################################################################################################################################

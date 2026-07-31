# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import GENERIC
from zato.common.hl7.fhir.fields import Outconn_Column_Defaults, Outconn_Opaque_Defaults, Outconn_Security_Id_Key, \
    Outconn_Security_Name_Key
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

class OutgoingFHIRImporter(GenericConnectionImporter):

    connection_type = GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR

    # What makes a row an outgoing FHIR connection rather than any other generic connection
    connection_defaults = dict(Outconn_Column_Defaults, **{
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
    })

    connection_extra_field_defaults = Outconn_Opaque_Defaults

    connection_secret_keys:'list' = []
    connection_required_attrs = ['name', 'address']

# ################################################################################################################################

    def resolve_references(self, connection_def:'anydict') -> 'None':
        """ Turns what a YAML definition names into what a connection stores, which is the id
        of the security definition its requests go out authenticated with.
        """
        self._resolve_security(connection_def)

# ################################################################################################################################

    def _resolve_security(self, connection_def:'anydict') -> 'None':
        """ A connection names the security definition it authenticates with, and what is stored is
        that definition's id, so the name is looked up and then dropped - it is not a field of the
        connection and must not reach the opaque attributes.
        """
        security_name = connection_def.pop(Outconn_Security_Name_Key, '')

        # A connection without one sends its requests unauthenticated
        if not security_name:
            return

        sec_def = self.importer.sec_defs.get(security_name)

        if not sec_def:
            name = connection_def['name']
            raise Exception(f'Security definition `{security_name}` not found for outgoing FHIR connection `{name}`')

        connection_def[Outconn_Security_Id_Key] = sec_def['id']

# ################################################################################################################################
# ################################################################################################################################

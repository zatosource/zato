# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.alerting.object_config import conn_type_to_alert_type
from zato.common.api import GENERIC, SchedulerLink
from zato.common.hl7.fhir.fields import Outgoing_Column_Defaults, Outgoing_Opaque_Defaults, Outgoing_Security_Id_Key, \
    Outgoing_Security_Name_Key
from zato.cli.enmasse.importers.generic import GenericConnectionImporter
from zato.cli.enmasse.util.delivery import prepare_delivery_fields

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

# How an error message names this kind of connection
_connection_type = 'outgoing FHIR'

# ################################################################################################################################
# ################################################################################################################################

class OutgoingFHIRImporter(GenericConnectionImporter):

    connection_type = GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR

    # What makes a row an outgoing FHIR connection rather than any other generic connection
    connection_defaults = dict(Outgoing_Column_Defaults, **{
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
    })

    connection_extra_field_defaults = Outgoing_Opaque_Defaults

    connection_secret_keys:'list' = []
    connection_required_attrs = ['name', 'address']

    # The alerts mapping of a FHIR connection follows the FHIR type - the REST settings plus the outcome codes
    alert_type = conn_type_to_alert_type[GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR]

    # A FHIR connection's health check job links back to it as a FHIR outgoing connection
    health_check_conn_type = SchedulerLink.ConnType.FHIR_Outgoing

# ################################################################################################################################

    def resolve_references(self, connection_def:'anydict') -> 'None':
        """ Turns what a YAML definition names into what a connection stores, which is the id
        of the security definition its requests go out authenticated with.
        """
        self._resolve_security(connection_def)

# ################################################################################################################################

    def validate_definition(self, connection_def:'anydict') -> 'None':
        """ The field list fills in and types the delivery fields on its own, what it does not do is reject a value
        the field does not take - a switch that is not a boolean, a negative count, an action that is not one of the four.
        """
        prepare_delivery_fields(connection_def, _connection_type)

# ################################################################################################################################

    def _resolve_security(self, connection_def:'anydict') -> 'None':
        """ A connection names the security definition it authenticates with, and what is stored is
        that definition's id, so the name is looked up and then dropped - it is not a field of the
        connection and must not reach the opaque attributes.
        """
        security_name = connection_def.pop(Outgoing_Security_Name_Key, '')

        # A connection without one sends its requests unauthenticated
        if not security_name:
            return

        sec_def = self.importer.sec_defs.get(security_name)

        if not sec_def:
            name = connection_def['name']
            raise Exception(f'Security definition `{security_name}` not found for outgoing FHIR connection `{name}`')

        connection_def[Outgoing_Security_Id_Key] = sec_def['id']

# ################################################################################################################################
# ################################################################################################################################

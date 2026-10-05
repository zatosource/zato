# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.alerting.object_config import conn_type_to_alert_type
from zato.common.api import GENERIC, HL7, SchedulerLink
from zato.common.destination.model import dump_entries, parse_entries
from zato.common.hl7.fhir.fields import Bulk_Export_Names, Outgoing_Column_Defaults, Outgoing_Opaque_Defaults, \
    Outgoing_Security_Id_Key, Outgoing_Security_Name_Key
from zato.cli.enmasse.importers.generic import GenericConnectionImporter
from zato.cli.enmasse.util.delivery import prepare_delivery_fields
from zato.cli.enmasse.util.invocation import sync_bulk_export_job

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict

    SASession = SASession
    any_ = any_
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

# How an error message names this kind of connection
_connection_type = 'outgoing FHIR'

_bulk = HL7.BulkExport

# The bulk export fields a hand-written file holds as lists, stored as one value per line
_bulk_list_fields = (_bulk.Field_Types, _bulk.Field_Type_Filter)
_bulk_list_separator = '\n'

# The bulk export field a hand-written file holds as a destination list of its own
_bulk_destinations_field = _bulk.Field_Destinations

# Every bulk export field a file may set - the job ID is environment-local and never travels through enmasse
_importable_bulk_names = set(Bulk_Export_Names) - {_bulk.Field_Job_ID}

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
        self._flatten_bulk_export(connection_def)

# ################################################################################################################################

    def validate_definition(self, connection_def:'anydict') -> 'None':
        """ The field list fills in and types the delivery fields on its own, what it does not do is reject a value
        the field does not take - a switch that is not a boolean, a negative count, an action that is not one of the four.
        """
        prepare_delivery_fields(connection_def, _connection_type)

# ################################################################################################################################

    def sync_linked_jobs(self, session:'SASession', merged_def:'anydict', connection:'any_') -> 'None':
        """ The bulk export job of the connection, if its definition schedules one.
        """
        sync_bulk_export_job(self.importer, session, merged_def, connection, self.health_check_conn_type)

# ################################################################################################################################

    def _flatten_bulk_export(self, connection_def:'anydict') -> 'None':
        """ A hand-written file keeps the Bulk export tab under one mapping of its own, while a connection
        stores each of its fields flat under a prefix - lists become one value per line and the destinations
        become the JSON text the Dashboard writes, one stored form no matter which of the two wrote it.
        """
        bulk_export = connection_def.pop(_bulk.Enmasse_Key, None)

        # A connection without the mapping keeps what each field defaults to
        if not bulk_export:
            return

        name = connection_def['name']

        for key, value in bulk_export.items():

            field_name = _bulk.Field_Prefix + key

            if field_name not in _importable_bulk_names:
                raise Exception(f'Outgoing FHIR connection `{name}` has an unknown bulk export field `{key}`')

            if field_name in _bulk_list_fields:
                if isinstance(value, list):
                    value = _bulk_list_separator.join(value)

            elif field_name == _bulk_destinations_field:
                entries = parse_entries(value)
                value = dump_entries(entries)

            connection_def[field_name] = value

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

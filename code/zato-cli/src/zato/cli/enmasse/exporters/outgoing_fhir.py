# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.cli.enmasse.util.alerts import group_alerts
from zato.cli.enmasse.util.invocation import Health_Check_Fields
from zato.common.alerting.object_config import Alerts_Key, conn_type_to_alert_type
from zato.common.api import GENERIC, HL7, HTTP_SOAP
from zato.common.destination.model import describe_entries, DestinationException, parse_entries
from zato.common.hl7.fhir.fields import Bulk_Export_Fields, Bulk_Export_Names, Outgoing_Fields, Outgoing_Security_Id_Key, \
    Outgoing_Security_Name_Key
from zato.common.odb.model import SecurityBase, to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.api import as_bool
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import any_, anydict, list_, stranydict

    any_ = any_
    stranydict = stranydict
    outgoing_fhir_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_alert_type = conn_type_to_alert_type[GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR]
_health_check = HTTP_SOAP.HealthCheck
_bulk = HL7.BulkExport

# The bulk export fields a file holds as lists, stored as one value per line or comma-separated
_bulk_list_fields = (_bulk.Field_Types, _bulk.Field_Type_Filter)
_bulk_list_separators = ('\n', ',')

# What a file keeps a bulk export's active flag and its destinations under
_bulk_is_active_key = _bulk.Field_Is_Active[len(_bulk.Field_Prefix):]

# ################################################################################################################################
# ################################################################################################################################

def _split_list_value(value:'str') -> 'list[str]':
    """ One value per line or comma-separated, as the Dashboard accepts either.
    """
    for separator in _bulk_list_separators:
        value = value.replace(separator, _bulk_list_separators[0])

    out = []

    for item in value.split(_bulk_list_separators[0]):
        item = item.strip()
        if item:
            out.append(item)

    return out

# ################################################################################################################################

def _describe_destinations(conn_name:'str', destinations:'any_') -> 'any_':
    """ Returns a connection's bulk export destinations in the form YAML holds them, which is a list
    of their own. A list that cannot be read is exported as it stands.
    """
    try:
        entries = parse_entries(destinations)
    except DestinationException as e:
        logger.warning('Exporting the bulk export destinations of `%s` as they stand; e:`%s`', conn_name, e)
        return destinations

    out = describe_entries(entries)
    return out

# ################################################################################################################################

def group_bulk_export(row:'anydict') -> 'stranydict':
    """ The Bulk export tab of a connection as one mapping of its own - every field the connection sets away
    from its default, with the prefix stripped off each key. An inactive export that sets nothing produces
    an empty mapping, so the block is left out of the file. The job ID is environment-local and never travels.
    """

    # Our response to produce
    out:'stranydict' = {}

    is_active = as_bool(row.get(_bulk.Field_Is_Active, False))

    for field in Bulk_Export_Fields:

        if field.name == _bulk.Field_Job_ID:
            continue

        value = row.get(field.name, field.default)

        # The active flag goes first when the export is on, the other fields only when they differ
        if field.name == _bulk.Field_Is_Active:
            if is_active:
                out[_bulk_is_active_key] = True
            continue

        if value == field.default:
            continue

        key = field.name[len(_bulk.Field_Prefix):]

        if field.name in _bulk_list_fields:
            value = _split_list_value(value)

        elif field.name == _bulk.Field_Destinations:
            value = _describe_destinations(row['name'], value)

        out[key] = value

    return out

# ################################################################################################################################
# ################################################################################################################################

class OutgoingFHIRExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def _get_security_name(self, session:'SASession', security_id:'int') -> 'str':
        """ Returns the name of the security definition with the given id, empty when the connection
        refers to one that has been deleted since - such a connection exports without a name rather
        than failing the whole export.
        """
        sec_def = session.query(SecurityBase).filter_by(id=security_id).first()

        if not sec_def:
            logger.info('No security definition with id %s, exporting the connection without one', security_id)
            return ''

        out = sec_def.name
        return out

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'outgoing_fhir_def_list':
        """ Exports outgoing HL7 FHIR connection definitions.
        """
        logger.info('Exporting outgoing HL7 FHIR definitions')

        db_items = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR)

        if not db_items:
            logger.info('No outgoing HL7 FHIR definitions found in DB')
            return []

        connections = to_json(db_items, return_as_dict=True)

        connection_count = len(connections)
        noun = 'definition' if connection_count == 1 else 'definitions'
        logger.debug('Processing %d outgoing HL7 FHIR %s', connection_count, noun)

        exported = []

        for row in connections:

            # Merge opaque attributes into the row so all fields are accessible at the top level ..
            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            # .. build the export item with the connection name, its address and whatever the connection
            # .. has been configured away from, so that a re-import reproduces it exactly ..
            item = {
                'name': row['name'],
                'address': row['address'],
            }

            for field in Outgoing_Fields:

                # .. the Bulk export tab's fields travel under one mapping of their own ..
                if field.name in Bulk_Export_Names:
                    continue

                value = row.get(field.name, field.default)

                if value == field.default:
                    continue

                # .. the security definition travels by name rather than by the id that is stored ..
                if field.name == Outgoing_Security_Id_Key:
                    security_name = self._get_security_name(session, value)
                    if security_name:
                        item[Outgoing_Security_Name_Key] = security_name
                    continue

                item[field.name] = value

            # .. a health check travels as how often it runs ..
            if row.get(_health_check.Field_Run_Every):
                for field_name in Health_Check_Fields:
                    item[field_name] = row[field_name]

            # .. the Bulk export tab goes under one mapping when the export is on or configured ..
            if bulk_export := group_bulk_export(row):
                item[_bulk.Enmasse_Key] = bulk_export

            # .. the alert settings the connection sets of its own go under one alerts mapping ..
            if alerts := group_alerts(row, _alert_type):
                item[Alerts_Key] = alerts

            # .. and add it to the output.
            exported.append(item)

        exported_count = len(exported)
        noun = 'definition' if exported_count == 1 else 'definitions'
        logger.info('Successfully prepared %d outgoing HL7 FHIR %s for export', exported_count, noun)
        return exported

# ################################################################################################################################
# ################################################################################################################################

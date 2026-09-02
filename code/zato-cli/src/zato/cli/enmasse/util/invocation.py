# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps as json_dumps, loads as json_loads

# Zato
from zato.common.api import HTTP_SOAP, SCHEDULER, SchedulerLink, URL_TYPE
from zato.common.odb.model import Job
from zato.common.util.imap_scheduler import interval_from_unit

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.typing_ import any_, anydict

    # Add dummy assignments to satisfy type checkers
    SASession = SASession
    EnmasseYAMLImporter = EnmasseYAMLImporter
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

_invocation = HTTP_SOAP.Invocation
_health_check = HTTP_SOAP.HealthCheck
_retry = HTTP_SOAP.Retry

# The retry config fields shared by outgoing REST and SOAP connections,
# each mapped to its shared default value.
Retry_Field_Defaults = {
    _retry.Field_Max_Retries: _retry.Default_Max_Retries,
    _retry.Field_Sleep_Time: _retry.Default_Sleep_Time,
    _retry.Field_Backoff_Threshold: _retry.Default_Backoff_Threshold,
    _retry.Field_Backoff_Multiplier: _retry.Default_Backoff_Multiplier,
}

Retry_Fields = tuple(Retry_Field_Defaults)

# Row-based invocation fields are YAML lists of {key, value, mode} mappings in enmasse files
# and JSON strings in the database.
Invocation_Row_Fields = (
    _invocation.Field_Request_Query_String,
    _invocation.Field_Request_Path_Params,
    _invocation.Field_Request_Headers,
    _invocation.Field_Request_Message,
    _invocation.Field_Request_SOAP_Headers,
)

# The invocation and health check fields shared by outgoing REST and SOAP connections.
# Job IDs are environment-local so they never travel through enmasse - the importer
# recreates the linked jobs itself.
Invocation_Common_Fields = (
    _invocation.Field_Response_Map,
    _invocation.Field_Response_Map_Mode,
    _invocation.Field_Callback_Type,
    _invocation.Field_Callback_Name,
    _invocation.Field_Run_Every,
    _invocation.Field_Run_Unit,
    _invocation.Field_Start_Date,
    _health_check.Field_Run_Every,
    _health_check.Field_Run_Unit,
    _health_check.Field_Notify_On,
    _health_check.Field_Callback_Type,
    _health_check.Field_Callback_Name,
)

# Everything an outgoing REST connection carries
Invocation_Fields_REST = (
    _invocation.Field_Request_Method,
    _invocation.Field_Request_Query_String,
    _invocation.Field_Request_Path_Params,
    _invocation.Field_Request_Headers,
    _invocation.Field_Request_Data,
    _invocation.Field_Request_Data_Mode,
) + Invocation_Common_Fields

# Everything an outgoing SOAP connection carries
Invocation_Fields_SOAP = (
    _invocation.Field_Request_Operation,
    _invocation.Field_Request_Message,
    _invocation.Field_Request_Message_Map,
    _invocation.Field_Request_SOAP_Headers,
    _invocation.Field_WSA_Action,
    _invocation.Field_WSA_To,
    _invocation.Field_WSA_Reply_To,
) + Invocation_Common_Fields

# ################################################################################################################################

def _as_order_fields(field_names:'any_') -> 'any_':
    """ Turns a tuple of invocation field names into FileWriter order notation,
    marking row-based fields with the :list suffix so they render as YAML lists.
    """

    # Our response to produce
    out = []

    for field_name in field_names:
        if field_name in Invocation_Row_Fields:
            out.append(field_name + ':list')
        else:
            out.append(field_name)

    return tuple(out)

# The same field lists in the notation the file writer's order tuples use
Invocation_Order_Fields_REST = _as_order_fields(Invocation_Fields_REST)
Invocation_Order_Fields_SOAP = _as_order_fields(Invocation_Fields_SOAP)

# ################################################################################################################################

def as_row_list(value:'any_') -> 'any_':
    """ Normalizes a row-based invocation field to a list of rows - the Dashboard stores them
    in the database as JSON strings while YAML files carry them as lists of mappings.
    """

    # Our response to produce
    out = []

    if value:
        if isinstance(value, str):
            out = json_loads(value)
        else:
            out = value

    return out

# ################################################################################################################################

def export_invocation_fields(exported_conn:'anydict', opaque:'anydict', field_names:'any_') -> 'None':
    """ Copies the declarative invocation and health check fields from a connection's opaque
    attributes to its exported definition, turning row-based fields into YAML-friendly lists.
    """
    for field_name in field_names:
        value = opaque.get(field_name)
        if not value:
            continue

        # Row fields become lists so enmasse files stay human-editable
        if field_name in Invocation_Row_Fields:
            value = as_row_list(value)
            if not value:
                continue

        exported_conn[field_name] = value

# ################################################################################################################################

def export_retry_fields(exported_conn:'anydict', opaque:'anydict') -> 'None':
    """ Copies the retry config fields from a connection's opaque attributes to its exported
    definition - only values different from the shared defaults are exported.
    """
    for field_name, default in Retry_Field_Defaults.items():

        # Connections that predate the retry config carry no values at all
        value = opaque.get(field_name)
        if value is None:
            continue

        # A value equal to the default would be redundant in an enmasse file
        if value != default:
            exported_conn[field_name] = value

# ################################################################################################################################

def serialize_invocation_rows(item:'anydict') -> 'None':
    """ Serializes the row-based invocation fields of a YAML definition back to the JSON strings
    the database keeps, ahead of the definition being stored.
    """
    for field_name in Invocation_Row_Fields:
        value = item.get(field_name)
        if value and not isinstance(value, str):

            rows = []

            for row in value:
                key = row['key']
                key = key.strip()

                if not key:
                    continue

                row = dict(row)
                row['key'] = key
                rows.append(row)

            item[field_name] = json_dumps(rows)

# ################################################################################################################################

def _sync_one_invocation_job(
    importer,    # type: EnmasseYAMLImporter
    session,     # type: SASession
    conn_def,    # type: anydict
    conn,        # type: any_
    kind,        # type: str
    conn_type,   # type: str
    job_name,    # type: str
    job_service, # type: str
    run_every,   # type: any_
    run_unit,    # type: str
    start_date,  # type: any_
    extra,       # type: str
    ) -> 'any_':
    """ Creates or updates one scheduler job linked to a connection being imported.
    """

    # Build a regular scheduler job definition out of the connection's fields,
    # carrying the generic link attributes that point back to the connection.
    job_def = {
        'name': job_name,
        'service': job_service,
        'job_type': SCHEDULER.JOB_TYPE.INTERVAL_BASED,
        'is_active': conn_def.get('is_active', True),
        'extra': extra,
        SchedulerLink.Conn_Type: conn_type,
        SchedulerLink.Conn_ID: conn.id,
        SchedulerLink.Kind: kind,
    }

    interval = interval_from_unit(int(run_every), run_unit)
    job_def.update(interval)

    if start_date:
        job_def['start_date'] = start_date

    # The job may already exist from a previous import, in which case it is updated in place
    existing_job = session.query(Job).filter_by(name=job_name, cluster_id=importer.cluster_id).first()

    if existing_job:
        job_def['id'] = existing_job.id
        out = importer.scheduler_importer.update_job_definition(job_def, session)
    else:
        out = importer.scheduler_importer.create_job_definition(job_def, session)

    return out

# ################################################################################################################################

def sync_invocation_jobs(
    importer,  # type: EnmasseYAMLImporter
    session,   # type: SASession
    conn_def,  # type: anydict
    conn,      # type: any_
    transport, # type: str
    ) -> 'None':
    """ Creates or updates the scheduled-invocation and health check jobs of an outgoing REST
    or SOAP connection being imported, storing the job IDs back in the definition so they land
    in the connection's opaque attributes. Job IDs never travel through enmasse files themselves.
    """
    if transport == URL_TYPE.SOAP:
        job_prefix = _invocation.Job_Prefix_SOAP
        conn_type = SchedulerLink.ConnType.SOAP_Outgoing
    else:
        job_prefix = _invocation.Job_Prefix_REST
        conn_type = SchedulerLink.ConnType.REST_Outgoing

    # The scheduled-invocation job runs the connection through the shared dispatch service ..
    if run_every := conn_def.get(_invocation.Field_Run_Every):

        run_unit = conn_def.get(_invocation.Field_Run_Unit)
        if not run_unit:
            run_unit = _invocation.Unit.Minutes
        conn_def[_invocation.Field_Run_Unit] = run_unit

        extra = json_dumps({
            _invocation.Extra_Conn_ID: conn.id,
            _invocation.Extra_Conn_Name: conn.name,
            _invocation.Extra_Transport: transport,
        })

        job = _sync_one_invocation_job(
            importer,
            session,
            conn_def,
            conn,
            kind=SchedulerLink.KindType.Scheduler,
            conn_type=conn_type,
            job_name=job_prefix + conn.name,
            job_service=_invocation.Dispatch_Service,
            run_every=run_every,
            run_unit=run_unit,
            start_date=conn_def.get(_invocation.Field_Start_Date),
            extra=extra,
        )
        conn_def[_invocation.Field_Job_ID] = job.id

    # .. and the health check job pings the connection, delivering each outcome to the callback.
    if health_check_run_every := conn_def.get(_health_check.Field_Run_Every):

        health_check_run_unit = conn_def.get(_health_check.Field_Run_Unit)
        if not health_check_run_unit:
            health_check_run_unit = _invocation.Unit.Minutes
        conn_def[_health_check.Field_Run_Unit] = health_check_run_unit

        notify_on = conn_def.get(_health_check.Field_Notify_On)
        if not notify_on:
            notify_on = _health_check.NotifyOn.Failures
        conn_def[_health_check.Field_Notify_On] = notify_on

        extra = json_dumps({
            _health_check.Extra_Conn_ID: conn.id,
            _health_check.Extra_Conn_Name: conn.name,
            _health_check.Extra_Conn_Type: conn_type,
            _health_check.Field_Callback_Type: conn_def.get(_health_check.Field_Callback_Type),
            _health_check.Field_Callback_Name: conn_def.get(_health_check.Field_Callback_Name),
            _health_check.Field_Notify_On: notify_on,
        })

        job = _sync_one_invocation_job(
            importer,
            session,
            conn_def,
            conn,
            kind=SchedulerLink.KindType.HealthCheck,
            conn_type=conn_type,
            job_name=_health_check.Job_Prefix + conn.name,
            job_service=_health_check.Dispatch_Service,
            run_every=health_check_run_every,
            run_unit=health_check_run_unit,
            start_date=None,
            extra=extra,
        )
        conn_def[_health_check.Field_Job_ID] = job.id

# ################################################################################################################################
# ################################################################################################################################

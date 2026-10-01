# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Azure
    Capacity_Name  = 'zatofabric'
    Resource_Group = 'zato-project-rg'
    Capacity_SKU   = 'F2'

    # App registrations
    App_Name             = 'Zato Fabric'
    Events_REST_App_Name = 'Zato Fabric Events REST'

    # State key prefix of the events REST registration
    Events_REST_Prefix = 'events_rest_'

    # State files
    State_Dir    = os.path.expanduser('~/env/fabric-live')
    State_File   = 'state.json'
    Enmasse_File = 'enmasse.yaml'
    INI_File     = 'fabric.ini'

    # Fabric items
    Workspace_Name             = 'Clinic Analytics'
    Lakehouse_Name             = 'Operations'
    Eventhouse_Name            = 'Operations Events'
    Events_Table               = 'Events'
    Eventstream_Name           = 'occupancy-events'
    Eventstream_Source         = 'zato'
    Eventstream_Alerts         = 'stock-alerts'
    Reminder_Notebook_Name     = 'Reminder candidates'
    Reminders_Pipeline_Name    = 'Reminders'
    Nightly_Notebook_Name      = 'Nightly occupancy'
    Nightly_Pipeline_Name      = 'Nightly occupancy'
    Occupancy_Model_Name       = 'Occupancy'
    Occupancy_Report_Name      = 'Occupancy'
    Appointments_Pipeline_Name = 'Appointments from clinic'

    # The Fabric connection the pipelines use
    Zato_Connection_Name = 'Zato'
    Zato_Connection_URL  = 'https://zato.example.com'

    # The header and its placeholder value a pipeline sends to a Zato REST channel
    API_Key_Header      = 'X-API-Key'
    API_Key_Placeholder = 'the key of the channel'

    # The event type the alerts destination receives
    Alert_Event_Type = 'stock_below_reorder'

    # Zato objects
    Connection_Name        = 'Zato Fabric'
    Events_Token_Name      = 'Fabric Events Token'
    Events_REST_Token_Name = 'Fabric Events REST Token'
    Events_Key_Name        = 'Fabric Events Key'
    Events_Outgoing_Name   = 'Fabric Events'
    Events_REST_Name       = 'Fabric Events REST'
    Alerts_Channel_Name    = 'Fabric Alerts'
    Alerts_Service_Name    = 'stock.notify-purchasing'

    # The PLAIN username of a connection string
    Plain_Username = '$$ConnectionString'

    # Tokens
    Token_URL_Template    = 'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    Events_Scope_Template = 'https://{namespace}/.default'
    Events_REST_Scope     = 'https://eventhubs.azure.net/.default'

    # The Kafka port of an Event Hubs namespace
    Kafka_Port = 9093

    # Sample tables
    Tables = 'locations', 'insurers', 'staff', 'admissions', 'occupancy', 'appointments', 'invoices', 'inventory'
    Locations = 'Riverside', 'Oak Hill', 'Maple Grove'

    # Files folders
    Incoming_Folder = 'Files/incoming'
    Exports_Folder  = 'Files/exports'

    # Timeouts
    Az_Timeout      = 120
    Az_Long_Timeout = 900

    Access_Timeout       = 300
    Access_Poll_Interval = 15

    Provisioning_Timeout       = 600
    Provisioning_Poll_Interval = 10

    # The variable that turns the tests' skip into a failure
    Required_Variable = 'Zato_Test_Fabric_Live'

# ################################################################################################################################
# ################################################################################################################################

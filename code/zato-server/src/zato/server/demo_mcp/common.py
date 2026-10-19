# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The names of the objects the MCP healthcare demo consists of - the importer, the remover
# and the deployed services all refer to the objects through these names.

# Zato
from zato.common.util.gateway import get_mcp_group_name

# ################################################################################################################################
# ################################################################################################################################

# The MCP gateway the healthcare network's data sources are exposed through
Gateway_Name        = 'demo.healthcare'
Gateway_Public_Name = 'Healthcare'
Gateway_URL_Path    = '/mcp/healthcare'

# The static bearer token MCP clients of the gateway authenticate with
Security_Name  = 'demo.healthcare.mcp'
Security_Token = 'healthcare-demo'

# The gateway's own security group, which the bearer token is a member of
Group_Name = get_mcp_group_name(Gateway_Name)

# One SQL connection per data source of the healthcare network
SQL_Warehouse  = 'demo.healthcare.warehouse'
SQL_Supplies   = 'demo.healthcare.supplies'
SQL_Scheduling = 'demo.healthcare.scheduling'

SQL_Connections = [SQL_Warehouse, SQL_Supplies, SQL_Scheduling]

# The SQLite database file behind each SQL connection
Database_Files = {
    SQL_Warehouse:  'warehouse.db',
    SQL_Supplies:   'supplies.db',
    SQL_Scheduling: 'scheduling.db',
}

# The directory under the server's work directory the database files are created in
Database_Directory = 'demo-healthcare'

# The services the gateway exposes as tools
Service_Network_Overview = 'healthcare.get-network-overview'
Service_List_Facilities     = 'healthcare.list-facilities'
Service_Visit_Volume     = 'healthcare.get-visit-volume'
Service_Supply_Alerts    = 'healthcare.get-supply-alerts'
Service_Staffing         = 'healthcare.get-staffing'
Service_Interface_Feeds  = 'healthcare.get-interface-feeds'

Service_Names = [
    Service_Network_Overview,
    Service_List_Facilities,
    Service_Visit_Volume,
    Service_Supply_Alerts,
    Service_Staffing,
    Service_Interface_Feeds,
]

# The file the services are deployed from in the hot-deployment directory
Services_File_Name = 'demo_healthcare_mcp.py'

# How many days of history the databases hold, counting back from the day of the import
History_Days = 28

# ################################################################################################################################
# ################################################################################################################################

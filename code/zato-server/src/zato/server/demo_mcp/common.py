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

# One SQL connection per executive reporting data source
SQL_Warehouse = 'demo.healthcare.warehouse'
SQL_Finance   = 'demo.healthcare.finance'
SQL_Workforce = 'demo.healthcare.workforce'

SQL_Connections = [SQL_Warehouse, SQL_Finance, SQL_Workforce]

# The SQLite database file behind each SQL connection
Database_Files = {
    SQL_Warehouse: 'warehouse.db',
    SQL_Finance:   'finance.db',
    SQL_Workforce: 'workforce.db',
}

# The directory under the server's work directory the database files are created in
Database_Directory = 'demo-healthcare'

# The executive reporting services the gateway exposes as tools
Service_Scorecard       = 'healthcare.get-scorecard'
Service_Care_Flow       = 'healthcare.track-care-flow'
Service_Daily_Care_Flow = 'healthcare.get-daily-care-flow'
Service_Quality         = 'healthcare.review-quality'
Service_Workforce       = 'healthcare.assess-workforce'
Service_Finance         = 'healthcare.track-finance'

# The lookup services listing the codes and names the reporting services take and return
Service_List_Facilities = 'healthcare.list-facilities'
Service_List_Regions    = 'healthcare.list-regions'
Service_List_Cities     = 'healthcare.list-cities'
Service_List_Measures   = 'healthcare.list-measures'

Service_Names = [
    Service_Scorecard,
    Service_Care_Flow,
    Service_Daily_Care_Flow,
    Service_Quality,
    Service_Workforce,
    Service_Finance,
    Service_List_Facilities,
    Service_List_Regions,
    Service_List_Cities,
    Service_List_Measures,
]

# The file the services are deployed from in the hot-deployment directory
Services_File_Name = 'demo_healthcare_mcp.py'

# How many days of history the databases hold, counting back from the day of the import
History_Days = 56

# ################################################################################################################################
# ################################################################################################################################

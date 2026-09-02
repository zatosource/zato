# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import csv
import io
from datetime import datetime, timezone

# Zato
from zato.common.api import MicrosoftFabric
from zato.common.typing_ import cast_
from zato.server.connection.cloud.microsoft_fabric.base import MicrosoftFabricBase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, dictlist

# ################################################################################################################################
# ################################################################################################################################

_default = MicrosoftFabric.Default

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftFabricTables(MicrosoftFabricBase):
    """ Lakehouse tables - listing them, loading files into them and writing rows directly.
    """

    def list_tables(self, workspace_id:'str', lakehouse_id:'str') -> 'anylist':
        """ Returns all the tables of a lakehouse.
        """
        path = f'/workspaces/{workspace_id}/lakehouses/{lakehouse_id}/tables'

        out:'anylist' = []

        # The listing is paged - collect the first page ..
        response = self.get(path)
        response = cast_('anydict', response)
        out.extend(response['data'])

        # .. and follow the continuation URIs until there are none.
        while continuation_uri := response.get('continuationUri'):
            response = self.get(continuation_uri)
            response = cast_('anydict', response)
            out.extend(response['data'])

        return out

# ################################################################################################################################

    def load_table(
        self,
        workspace_id:'str',
        lakehouse_id:'str',
        table_name:'str',
        relative_path:'str',
        mode:'str'='Overwrite',
        file_format:'str'='Csv',
        header:'bool'=True,
        delimiter:'str'=',',
        path_type:'str'='File',
        recursive:'bool'=False,
        ) -> 'str':
        """ Starts a load of a file or folder into a lakehouse table.
        Returns the address the operation can be tracked at, e.g. with wait_for_operation.
        """

        # CSV files carry their own options, other formats only need their name.
        if file_format == 'Csv':
            format_options = {'format': 'Csv', 'header': header, 'delimiter': delimiter}
        else:
            format_options = {'format': file_format}

        request_data = {
            'relativePath': relative_path,
            'pathType': path_type,
            'mode': mode,
            'recursive': recursive,
            'formatOptions': format_options,
        }

        # Start the load, which is a long-running operation ..
        path = f'/workspaces/{workspace_id}/lakehouses/{lakehouse_id}/tables/{table_name}/load'
        response = self.invoke_raw('POST', path, data=request_data)

        # .. whose status endpoint comes back in the Location header.
        out = response.headers['Location']
        return out

# ################################################################################################################################

    def write_table(
        self,
        workspace_id:'str',
        lakehouse_id:'str',
        table_name:'str',
        rows:'dictlist',
        mode:'str'='Overwrite',
        ) -> 'anydict':
        """ Writes a list of dicts to a lakehouse table - the rows travel as CSV files through OneLake
        and a single load operation turns them into the table's data. Returns the completed operation.
        """

        # All the rows share the columns of the first one.
        first_row = rows[0]
        field_names = list(first_row)

        # Each call writes to its own directory, named after the current time.
        now = datetime.now(timezone.utc)
        timestamp = now.strftime('%Y%m%d%H%M%S%f')
        relative_path = f'{_default.Table_Files_Prefix}/{table_name}/{timestamp}'

        # Write the rows in chunks, each chunk into its own CSV file ..
        chunk_size = _default.Table_Chunk_Rows
        row_count = len(rows)
        file_index = 0

        for chunk_start in range(0, row_count, chunk_size):
            chunk_end = chunk_start + chunk_size
            chunk = rows[chunk_start:chunk_end]

            # .. serialize this chunk to CSV ..
            buffer = io.StringIO()
            writer = csv.DictWriter(buffer, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(chunk)

            text = buffer.getvalue()
            data = text.encode('utf-8')

            # .. and place it in the lakehouse's files section.
            file_path = f'{lakehouse_id}/{relative_path}/part-{file_index:05}.csv'
            self.onelake_write(workspace_id, file_path, data)
            file_index += 1

        # Load the whole directory into the table in one operation ..
        location = self.load_table(workspace_id, lakehouse_id, table_name, relative_path,
            mode=mode, path_type='Folder', recursive=True)

        # .. and wait until the load completes.
        out = self.wait_for_operation(location)

        return out

# ################################################################################################################################
# ################################################################################################################################

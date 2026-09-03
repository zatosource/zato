# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.typing_ import cast_
from zato.server.connection.cloud.microsoft_fabric.spark import MicrosoftFabricSpark

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anydictnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftFabricClient(MicrosoftFabricSpark):
    """ Client for Microsoft Fabric APIs, using the OAuth2 client credentials grant.
    """

    def list_workspaces(self) -> 'anydict':
        """ Returns all the workspaces the connection's principal has access to.
        """
        response = self.get('/workspaces')

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def get_workspace(self, workspace_id:'str') -> 'anydict':
        """ Returns details of a single workspace.
        """
        response = self.get(f'/workspaces/{workspace_id}')

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def create_workspace(self, name:'str', description:'str'='') -> 'anydict':
        """ Creates a new workspace.
        """
        request_data = {'displayName': name}
        if description:
            request_data['description'] = description

        response = self.post('/workspaces', data=request_data)

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def delete_workspace(self, workspace_id:'str') -> 'None':
        """ Deletes a workspace.
        """
        _ = self.delete(f'/workspaces/{workspace_id}')

# ################################################################################################################################

    def list_items(self, workspace_id:'str', item_type:'str'='') -> 'anydict':
        """ Returns items in a workspace, optionally filtered by their type, e.g. Lakehouse or Notebook.
        """
        if item_type:
            params = {'type': item_type}
        else:
            params = None

        response = self.get(f'/workspaces/{workspace_id}/items', params=params)

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def get_item(self, workspace_id:'str', item_id:'str') -> 'anydict':
        """ Returns details of a single item in a workspace.
        """
        response = self.get(f'/workspaces/{workspace_id}/items/{item_id}')

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def create_item(self, workspace_id:'str', name:'str', item_type:'str', description:'str'='') -> 'anydict':
        """ Creates a new item in a workspace, e.g. a lakehouse or a notebook.
        """
        request_data = {'displayName': name, 'type': item_type}
        if description:
            request_data['description'] = description

        response = self.post(f'/workspaces/{workspace_id}/items', data=request_data)

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def update_item(self, workspace_id:'str', item_id:'str', data:'anydict') -> 'anydict':
        """ Updates an item in a workspace, e.g. its display name or description.
        """
        response = self.patch(f'/workspaces/{workspace_id}/items/{item_id}', data=data)

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def delete_item(self, workspace_id:'str', item_id:'str') -> 'None':
        """ Deletes an item from a workspace.
        """
        _ = self.delete(f'/workspaces/{workspace_id}/items/{item_id}')

# ################################################################################################################################

    def run_job(self, workspace_id:'str', item_id:'str', job_type:'str', payload:'anydictnone'=None) -> 'str':
        """ Runs an item's job on demand, e.g. executes a notebook or a data pipeline.
        Returns the ID of the new job instance, e.g. for use with get_job.
        """
        params = {'jobType': job_type}
        path = f'/workspaces/{workspace_id}/items/{item_id}/jobs/instances'

        # Start the job, which is a long-running operation ..
        response = self.invoke_raw('POST', path, params=params, data=payload)

        # .. the new job's address comes back in the Location header ..
        location = response.headers['Location']

        # .. and its ID is the last path segment.
        location = location.rstrip('/')
        segments = location.split('/')

        out = segments[-1]
        return out

# ################################################################################################################################

    def get_job(self, workspace_id:'str', item_id:'str', job_id:'str') -> 'anydict':
        """ Returns details of a single job instance of an item.
        """
        response = self.get(f'/workspaces/{workspace_id}/items/{item_id}/jobs/instances/{job_id}')

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def cancel_job(self, workspace_id:'str', item_id:'str', job_id:'str') -> 'None':
        """ Cancels a job instance of an item.
        """
        _ = self.post(f'/workspaces/{workspace_id}/items/{item_id}/jobs/instances/{job_id}/cancel')

# ################################################################################################################################

    def list_shortcuts(self, workspace_id:'str', item_id:'str') -> 'anydict':
        """ Returns OneLake shortcuts defined in an item.
        """
        response = self.get(f'/workspaces/{workspace_id}/items/{item_id}/shortcuts')

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def create_shortcut(self, workspace_id:'str', item_id:'str', data:'anydict') -> 'anydict':
        """ Creates a OneLake shortcut in an item.
        """
        response = self.post(f'/workspaces/{workspace_id}/items/{item_id}/shortcuts', data=data)

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def delete_shortcut(self, workspace_id:'str', item_id:'str', shortcut_path:'str', shortcut_name:'str') -> 'None':
        """ Deletes a OneLake shortcut from an item.
        """
        _ = self.delete(f'/workspaces/{workspace_id}/items/{item_id}/shortcuts/{shortcut_path}/{shortcut_name}')

# ################################################################################################################################

    def list_capacities(self) -> 'anydict':
        """ Returns all the capacities the connection's principal has access to.
        """
        response = self.get('/capacities')

        out = cast_('anydict', response)
        return out

# ################################################################################################################################

    def zato_delete_impl(self, reason:'str'='') -> 'None':
        """ Closes the Spark sessions and the underlying HTTP session when the connection is deleted.
        """

        # Close each Spark session that is still open ..
        for session_key in list(self._spark_sessions):
            workspace_id, lakehouse_id = session_key.split('/', 1)
            try:
                self.close_spark_session(workspace_id, lakehouse_id)
            except Exception:
                logger.warning('Could not close a Spark session (%s) -> %s', self.name, format_exc())

        # .. and close the HTTP session itself.
        self.session.close()

# ################################################################################################################################

    def ping(self) -> 'None':
        """ Confirms that the connection's credentials are valid by listing its workspaces.
        """
        response = self.list_workspaces()
        workspaces = response['value']

        workspace_count = len(workspaces)
        suffix = 'workspace' if workspace_count == 1 else 'workspaces'

        logger.info('Microsoft Fabric ping OK (%s) -> %d %s', self.name, workspace_count, suffix)

# ################################################################################################################################
# ################################################################################################################################

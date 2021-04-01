# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class FileTransferChannel(object):
    def __init__(self):
        self._config_attrs = []
        self.id   = None      # type: int
        self.name = None      # type: str
        self.is_active = None # type: bool

        self.is_hot_deploy = None # type: bool
        self.source_type = None   # type: str
        self.pickup_from = ''     # type: str
        self.parse_with = ''      # type: str
        self.ftp_source_id = None # type: int
        self.line_by_line = None  # type: bool
        self.file_patterns = ''   # type: str

        self.service_list = None      # type: list
        self.topic_list = None        # type: list
        self.outconn_rest_list = None # type: list

        self.read_on_pickup = None  # type: bool
        self.sftp_source_id = None  # type: int
        self.parse_on_pickup = None # type: bool

        self.ftp_source_name = ''  # type: str
        self.sftp_source_name = '' # type: str

        self.service_list_json = None      # type: str
        self.topic_list_json = None        # type: str
        self.outconn_rest_list_json = None # type: str

        self.scheduler_job_id = None    # type: int
        self.move_processed_to = ''     # type: str
        self.delete_after_pickup = None # type: bool

# ################################################################################################################################

    def to_dict(self):
        out = {}
        for name in self._config_attrs:
            value = getattr(self, name)
            out[name] = value
        return out

# ################################################################################################################################

    @staticmethod
    def from_dict(config):
        # type: (dict) -> FileTransferChannel
        out = FileTransferChannel()
        for k, v in config.items():
            out._config_attrs.append(k)
            setattr(out, k, v)
        return out

# ################################################################################################################################
# ################################################################################################################################

# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from live_windows.settings import Accounts

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

class Shares:
    """ The data shares of each guest. Every guest has all of them.
    """

    # The folders of the hub, one outbox and one inbox per application
    Exchange = 'exchange'

    # Documents to distribute, their dated archive and the drop of the partner that receives them
    Documents    = 'documents'
    Archive      = 'archive'
    Partner_Drop = 'partner-drop'

    # Shipment notices and the label trigger files written for them
    Shipping = 'shipping'
    Labels   = 'labels'

    # The landing zone of the daily extracts, which requires SMB 3 encryption
    Landing = 'landing'

    # The folders exchanged in both directions between the HR and ERP applications
    People = 'people'

    All = Exchange, Documents, Archive, Partner_Drop, Shipping, Labels, Landing, People

    # The shares that only accept encrypted sessions
    Encrypted = Landing,

# ################################################################################################################################
# ################################################################################################################################

class Hub:

    # The environment the hub folders belong to
    Environment = 'test'

    # The applications that exchange files through the hub
    Plant     = 'plant'
    Logistics = 'logistics'
    Catalog   = 'catalog'

    Branches = 'branch01', 'branch02', 'branch03', 'branch04', 'branch05', 'branch06', 'branch07', 'branch08'

    Apps = (Plant, Logistics, Catalog) + Branches

    # The applications that the files of each application are routed to, the same table as in the routing service
    Routes = {
        Plant: (Logistics,),
        Logistics: (Plant,),
        Catalog: Branches,
        'branch01': (Logistics,),
        'branch02': (Logistics,),
        'branch03': (Logistics,),
        'branch04': (Logistics,),
        'branch05': (Logistics,),
        'branch06': (Logistics,),
        'branch07': (Logistics,),
        'branch08': (Logistics,),
    }

    # The folders of each application
    Outbox = 'outbox'
    Inbox  = 'inbox'

    # Where the hub moves the files it processed or rejected, relative to each outbox
    Processed = 'processed'
    Rejected  = 'rejected'

    # The suffix of a file the hub writes before it renames it to its final name
    Lock_Suffix = '.lck'

    # The suffix of each file the hub writes
    Out_Suffix = '.hub'

    # The number of digits of each sequence number
    Sequence_Digits = 6

# ################################################################################################################################
# ################################################################################################################################

class Folders:

    # The folders of the documents, shipping, labels, landing and people shares
    Documents_Outbox = 'outbox'
    Shipping_Outbox  = 'outbox'
    Label_Sites      = 'site-a', 'site-b'
    Label_Failed     = 'failed'
    Landing_Daily    = 'daily'
    HR_Outbound      = 'hr-outbound'
    HR_Inbound       = 'hr-inbound'
    ERP_Outbound     = 'erp-outbound'
    ERP_Inbound      = 'erp-inbound'

    People = HR_Outbound, HR_Inbound, ERP_Outbound, ERP_Inbound

# ################################################################################################################################
# ################################################################################################################################

class Local:

    # The directory on each guest under which every data share has its own directory
    Data_Root = r'C:\shares\data'

# ################################################################################################################################
# ################################################################################################################################

def share_local_path(share:'str') -> 'str':
    """ Returns the directory on the guest that a data share publishes.
    """
    out = f'{Local.Data_Root}\\{share}'
    return out

# ################################################################################################################################

def local_path(share:'str', path:'str') -> 'str':
    """ Returns the directory on the guest of a path inside a data share, given with forward slashes.
    """
    root = share_local_path(share)
    path = path.replace('/', '\\')

    out = f'{root}\\{path}'
    return out

# ################################################################################################################################

def app_folder(app:'str', folder:'str') -> 'str':
    """ Returns the path of the outbox or inbox of an application, relative to the exchange share.
    """
    out = f'{Hub.Environment}/apps/{app}/{folder}'
    return out

# ################################################################################################################################

def remote_path(share:'str', path:'str') -> 'str':
    """ Returns a path in the form that SMB connections in Zato use, with the share as its first element.
    """
    out = f'{share}/{path}'
    return out

# ################################################################################################################################

def sequence_name(sequence:'int', app:'str') -> 'str':
    """ Returns the name of a file an application writes into its outbox, e.g. 000012.plant.
    """
    out = f'{sequence:0{Hub.Sequence_Digits}d}.{app}'
    return out

# ################################################################################################################################

def _directories() -> 'strlist':
    """ Returns every directory the guests need under their data shares.
    """
    out:'strlist' = []

    for app in Hub.Apps:
        for folder in Hub.Outbox, Hub.Inbox:
            path = app_folder(app, folder)
            directory = local_path(Shares.Exchange, path)
            out.append(directory)

    out.append(local_path(Shares.Documents, Folders.Documents_Outbox))
    out.append(local_path(Shares.Shipping, Folders.Shipping_Outbox))
    out.append(local_path(Shares.Landing, Folders.Landing_Daily))

    for site in Folders.Label_Sites:
        out.append(local_path(Shares.Labels, site))

    for folder in Folders.People:
        out.append(local_path(Shares.People, folder))

    return out

# ################################################################################################################################

def _shares() -> 'anylist':
    """ Returns the definition of every data share, the access of each account included.
    """
    out:'anylist' = []

    for name in Shares.All:
        is_encrypted = name in Shares.Encrypted

        share = {
            'name': name,
            'path': share_local_path(name),
            'encrypt': is_encrypted,
            'change': [Accounts.Exchange_Username, Accounts.Harness_Username],
            'read': [],
        }
        out.append(share)

    return out

# ################################################################################################################################

def layout_command() -> 'anydict':
    """ Returns the fields of the command that makes the agent create the accounts, directories and shares.
    """
    users = [{
        'name': Accounts.Exchange_Username,
        'password': Accounts.Exchange_Password,
    }]

    out = {
        'users': users,
        'directories': _directories(),
        'shares': _shares(),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

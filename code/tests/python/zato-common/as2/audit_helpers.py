# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import AuditSource, event_table, get_audit_engine
from zato.common.ext.bunch import Bunch
from zato.common.json_internal import loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

Sender_Identifier   = 'ZatoRetail'
Receiver_Identifier = 'PartnerCorp'

Payload = (
    b'ISA*00*          *00*          *ZZ*ZATORETAIL     *ZZ*PARTNERCORP    '
    + b'*260709*1200*U*00401*000000001*0*P*>~GS*PO*ZATORETAIL*PARTNERCORP*20260709*1200*1*X*004010~'
    + b'ST*850*0001~BEG*00*NE*4523891**20260709~SE*3*0001~GE*1*1~IEA*1*000000001~'
)

# ################################################################################################################################
# ################################################################################################################################

def key_to_pem(key:'any_') -> 'any_':
    """ Serializes a private key the way the Dashboard stores it in a connection's configuration.
    """
    encryption = NoEncryption()

    serialized = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, encryption)

    out = serialized.decode('ascii')
    return out

# ################################################################################################################################

def certificate_to_pem(certificate:'any_') -> 'any_':
    """ Serializes a certificate the way the Dashboard stores it in a connection's configuration.
    """
    serialized = certificate.public_bytes(Encoding.PEM)

    out = serialized.decode('ascii')
    return out

# ################################################################################################################################

def load_events(event_type:'any_' = None) -> 'anylist':
    """ Reads all the AS2 audit events back from the per-test database, oldest first.
    """
    statement = select(
        event_table.c.event_type,
        event_table.c.object_name,
        event_table.c.msg_id,
        event_table.c.cid,
        event_table.c.correl_id,
        event_table.c.outcome,
        event_table.c.data,
    ).where(event_table.c.source == AuditSource.AS2).order_by(event_table.c.id)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        rows = result.fetchall()

    out = []

    for row in rows:
        item = Bunch()
        item.event_type = row[0]
        item.object_name = row[1]
        item.msg_id = row[2]
        item.cid = row[3]
        item.correl_id = row[4]
        item.outcome = row[5]
        item.details = loads(row[6])

        if event_type:
            if item.event_type != event_type:
                continue

        out.append(item)

    return out

# ################################################################################################################################
# ################################################################################################################################

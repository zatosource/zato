"""gh110 HTTP channels audit

Revision ID: 3f03ae0ef253
Revises: 45c5b38b620e
Create Date: 2013-11-27 20:54:35.653604

"""

# revision identifiers, used by Alembic.
revision = '3f03ae0ef253'
down_revision = '45c5b38b620e'

from alembic import op
import sqlalchemy as sa

# Zato
from zato.common import MISC, MSG_PATTERN_TYPE
from zato.common.odb import model

def upgrade():

    op.add_column(model.HTTPSOAP.__tablename__,
        sa.Column('audit_enabled', sa.Boolean(), nullable=False, default=False)
    )
    
    op.add_column(model.HTTPSOAP.__tablename__,
        sa.Column('audit_back_log', sa.Integer(), nullable=False, default=MISC.DEFAULT_AUDIT_BACK_LOG)
    )
    
    op.add_column(model.HTTPSOAP.__tablename__,
        sa.Column('audit_max_payload', sa.Integer(), nullable=False, default=MISC.DEFAULT_AUDIT_MAX_PAYLOAD)
    )
    
    op.add_column(model.HTTPSOAP.__tablename__,
        sa.Column('audit_repl_patt_type', sa.String(), nullable=False, default=MSG_PATTERN_TYPE.ELEM_PATH.id)
    )
    
    op.create_table(
        'http_soap_audit',
        sa.Column('id', sa.Integer, sa.Sequence('http_soap_audit_seq'), primary_key=True),
        sa.Column('cluster_id', sa.Integer, sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False, primary_key=False),
        sa.Column('cid', sa.String, nullable=False, index=True),
        sa.Column('name', sa.String, nullable=False, index=True),
        sa.Column('transport', sa.String, nullable=False, index=True),
        sa.Column('connection', sa.String, nullable=False, index=True),
        sa.Column('req_time', sa.DateTime, nullable=False),
        sa.Column('resp_time', sa.DateTime, nullable=True),
        sa.Column('user_token', sa.String, nullable=True, index=True),
        sa.Column('invoke_ok', sa.Boolean, nullable=True),
        sa.Column('auth_ok', sa.Boolean, nullable=True),
        sa.Column('user_token', sa.String, nullable=False, index=True),
        sa.Column('remote_addr', sa.String, nullable=False, index=True),
        sa.Column('req_headers', sa.String, nullable=True, index=True),
        sa.Column('req_payload', sa.String, nullable=True, index=True),
        sa.Column('resp_headers', sa.String, nullable=True, index=True),
        sa.Column('resp_payload', sa.String, nullable=True, index=True),
    )
    
    op.create_table(
        'http_soap_au_rpl_p_ep',
        sa.Column('id', sa.Integer, sa.Sequence('htp_sp_ad_rpl_p_ep_seq'), primary_key=True),
        sa.Column('conn_id', sa.Integer, sa.ForeignKey('http_soap.id', ondelete='CASCADE'), nullable=False),
        sa.Column('pattern_id', sa.Integer, sa.ForeignKey('msg_elem_path.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cluster_id', sa.Integer, sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
    )
    
    op.create_table(
        'http_soap_au_rpl_p_xp',
        sa.Column('id', sa.Integer, sa.Sequence('htp_sp_ad_rpl_p_xp_seq'), primary_key=True),
        sa.Column('conn_id', sa.Integer, sa.ForeignKey('http_soap.id', ondelete='CASCADE'), nullable=False),
        sa.Column('pattern_id', sa.Integer, sa.ForeignKey('msg_elem_path.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cluster_id', sa.Integer, sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
    )

def downgrade():
    op.drop_column(model.HTTPSOAP.__tablename__, 'audit_enabled')
    op.drop_column(model.HTTPSOAP.__tablename__, 'audit_back_log')
    op.drop_column(model.HTTPSOAP.__tablename__, 'audit_max_payload')
    op.drop_column(model.HTTPSOAP.__tablename__, 'audit_repl_patt_type')
    
    op.drop_table('http_soap_audit')
    op.drop_table('http_soap_ad_rpl_p_ep')
    op.drop_table('http_soap_ad_rpl_p_xp')

"""gh281 imap

Revision ID: 0016_6669bb02
Revises: 0015_f67f3ea1
Create Date: 2014-07-05 20:53:05

"""

# revision identifiers, used by Alembic.
revision = '0016_6669bb02'
down_revision = '0015_f67f3ea1'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence, DropSequence

# Zato
from zato.common.odb import model

def upgrade():
    op.execute(CreateSequence(sa.Sequence('email_imap_seq')))
    op.execute(CreateSequence(sa.Sequence('email_smtp_seq')))
    
    op.create_table(
        model.IMAP.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('email_imap_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('host', sa.String(400), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False),
        sa.Column('timeout', sa.Integer(), nullable=False),
        sa.Column('debug_level', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(400), nullable=True),
        sa.Column('password', sa.String(400), nullable=True),
        sa.Column('mode', sa.String(20), nullable=False),
        sa.Column('get_criteria', sa.String(2000), nullable=False),
        sa.Column('cluster_id', sa.Integer(), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        )        
    op.create_unique_constraint(
        'email_imap_name_cluster_id_key', model.IMAP.__tablename__, ['name', 'cluster_id']
        )
    
    op.drop_column(model.TLSKeyCertSecurity.__tablename__, 'cert_cn')    
    op.add_column(model.TLSKeyCertSecurity.__tablename__, sa.Column('cert_subject', sa.String(1200), nullable=False))
    
    op.drop_constraint('sec_tls_key_cert_id_fkey', model.TLSKeyCertSecurity.__tablename__)
    op.create_foreign_key('sec_tls_key_cert_id_fkey', model.TLSKeyCertSecurity.__tablename__, 'sec_base', ['id'], ['id'])
    

    
def downgrade():
    op.drop_table(model.IMAP.__tablename__)
    op.execute(DropSequence(sa.Sequence('email_imap_seq')))
    op.execute(DropSequence(sa.Sequence('email_smtp_seq')))
    op.drop_column(model.TLSKeyCertSecurity.__tablename__, 'cert_subject')    
    op.add_column(model.TLSKeyCertSecurity.__tablename__, sa.Column('cert_cn', sa.String(1200), nullable=False))

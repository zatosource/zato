"""gh289 tls validate server certs

Revision ID: 0019_e77a8c06
Revises: 0018_ed18fc6a
Create Date: 2014-07-24 15:00:05

"""

# revision identifiers, used by Alembic.
revision = '0019_e77a8c06'
down_revision = '0018_ed18fc6a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence, DropSequence

# Zato
from zato.common.odb import model

# ################################################################################################################################

def upgrade():
    op.execute(CreateSequence(sa.Sequence('search_solr_seq')))   
    op.create_table(
        model.Solr.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('search_solr_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('address', sa.String(400), nullable=False),
        sa.Column('timeout', sa.Integer(), nullable=False),
        sa.Column('ping_path', sa.String(40), nullable=False),
        sa.Column('options', sa.String(800), nullable=True),
        sa.Column('pool_size', sa.Integer(), nullable=False),
        sa.Column('cluster_id', sa.Integer, sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        )
        
    op.create_unique_constraint(
        'search_solr_name_cluster_id_key', 'search_solr', ['name', 'cluster_id']
        )
       
    op.execute(CreateSequence(sa.Sequence('sec_tls_ca_cert_seq')))
    op.create_table(
        model.TLSCACert.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('sec_tls_ca_cert_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('fs_name', sa.String(200), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        )
    
    op.add_column(
        model.HTTPSOAP.__tablename__, sa.Column(
            'sec_tls_ca_cert_id', sa.Integer(), sa.ForeignKey('sec_tls_ca_cert.id', ondelete='CASCADE'), nullable=True))
            
def downgrade():
    op.execute(DropSequence(sa.Sequence('search_solr_seq')))
    op.execute(DropSequence(sa.Sequence('sec_tls_ca_cert_seq')))
    op.drop_column(model.HTTPSOAP.__tablename__, 'sec_tls_ca_cert_id')
    op.drop_constraint('search_solr_name_cluster_id_key', 'search_solr')
    op.drop_table(model.Solr.__tablename__)
    op.drop_table(model.TLSCACert.__tablename__)

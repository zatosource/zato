"""gh265-271 Cassandra

Revision ID: 0013_6e651e7a3c38
Revises: 0012_c70a22206a1
Create Date: 2014-06-26 00:44:32

"""

# revision identifiers, used by Alembic.
revision = '0013_6e651e7a3c38'
down_revision = '0012_c70a22206a1'

from alembic import op
import sqlalchemy as sa

# Zato
from zato.common import CASSANDRA
from zato.common.odb import model

def upgrade():
    op.create_table(model.CassandraConn.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('conn_def_cassandra_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('contact_points', sa.String(400), nullable=False, default=CASSANDRA.DEFAULT.CONTACT_POINTS.value),
        sa.Column('port', sa.Integer(), nullable=False, default=CASSANDRA.DEFAULT.PORT.value),
        sa.Column('exec_size', sa.Integer(), nullable=False, default=CASSANDRA.DEFAULT.EXEC_SIZE.value),
        sa.Column('proto_version', sa.Integer(), nullable=False, default=CASSANDRA.DEFAULT.PROTOCOL_VERSION.value),
        sa.Column('cql_version', sa.Integer(), nullable=True),
        sa.Column('default_keyspace', sa.String(400), nullable=False),
        sa.Column('username', sa.String(200), nullable=True),
        sa.Column('password', sa.String(200), nullable=True),
        sa.Column('tls_ca_certs', sa.String(200), nullable=True),
        sa.Column('tls_client_cert', sa.String(200), nullable=True),
        sa.Column('tls_client_priv_key', sa.String(200), nullable=True),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False))

    op.create_table(model.CassandraQuery.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('query_cassandra_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('value', sa.LargeBinary(40000), nullable=False),
        sa.Column('def_id', sa.Integer(), sa.ForeignKey('conn_def_cassandra.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False))

def downgrade():
    op.drop_table(model.CassandraQuery.__tablename__)
    op.drop_table(model.CassandraConn.__tablename__)

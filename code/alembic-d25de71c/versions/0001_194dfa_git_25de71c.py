"""Upgrading from d25de71c to 3.0.

Revision ID: 0001_194dfa_git_25de71c
Revises: None
Create Date: 2017-08-17 11:43:00.833139

"""

# revision identifiers, used by Alembic.
revision = '0001_194dfa_git_25de71c'
down_revision = None

from alembic import context, op
import sqlalchemy as sa

# Zato
from zato.common.odb import model

def is_sqlite():
    config = context.config.get_section('alembic')
    return 'sqlite' in config.get('sqlalchemy.url').lower()

def upgrade():

    #
    # Commits
    #
    # 3db4b067419a5186cf2621b2c79cb476030e3c9d
    # 08a3c37e655d9138d23944ca95d514896a4aa22c
    # 4fb0946b630012538f1cdb975ec50b2aa1b48ba9
    # 60999acb9ed287b27acd9ef2f4cced727297049e
    #

    # Drop old tables
    op.drop_table(model.OutgoingAMQP.__tablename__)
    op.drop_table(model.ChannelAMQP.__tablename__)
    op.drop_table(model.ConnDefAMQP.__tablename__)

    # Recreate in reverse order so that foreign keys can be added in op.create_table operation

    # Connection definitions
    op.create_table(
        model.ConnDefAMQP.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('conn_def_amqp_seq'), nullable=False, primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('host', sa.String(200), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False),
        sa.Column('vhost', sa.String(200), nullable=False),
        sa.Column('username', sa.String(200), nullable=False),
        sa.Column('password', sa.String(200), nullable=False),
        sa.Column('frame_max', sa.Integer(), nullable=False),
        sa.Column('heartbeat', sa.Integer(), nullable=False),

        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', name='conn_def_cluster_id_fkey'), nullable=False),
        )

    # Channels
    op.create_table(
        model.ChannelAMQP.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('channel_amqp_seq'), nullable=False, primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('queue', sa.String(20), nullable=False),
        sa.Column('consumer_tag_prefix', sa.String(200), nullable=False),
        sa.Column('pool_size', sa.Integer(), nullable=False),
        sa.Column('ack_mode', sa.String(20), nullable=False),
        sa.Column('data_format', sa.String(20), nullable=True),

        sa.Column('def_id', sa.Integer(),
            sa.ForeignKey('conn_def_amqp.id', name='chan_conn_def_amqp_fkey', ondelete='CASCADE'), nullable=False),

        sa.Column('service_id', sa.Integer(),
            sa.ForeignKey('service.id', name='chan_amqp_service_id_fkey', ondelete='CASCADE'), nullable=False),
        )

    # Outgoing connections
    op.create_table(
        model.OutgoingAMQP.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('out_amqp_seq'), nullable=False, primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('delivery_mode', sa.SmallInteger(), nullable=False),
        sa.Column('priority', sa.SmallInteger(), nullable=False, default='5'),
        sa.Column('content_type', sa.String(200), nullable=True),
        sa.Column('content_encoding', sa.String(200), nullable=True),
        sa.Column('expiration', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.String(200), nullable=True),
        sa.Column('app_id', sa.String(200), nullable=True),
        sa.Column('pool_size', sa.SmallInteger(), nullable=False),

        sa.Column('def_id', sa.Integer(),
            sa.ForeignKey('conn_def_amqp.id', name='out_conn_def_amqp_fkey', ondelete='CASCADE'), nullable=False),
    )

    # SQLite doesn't support these operations

    if not is_sqlite():
        op.create_unique_constraint('conn_def_amqp_uq1', model.ConnDefAMQP.__tablename__, ['name', 'cluster_id'])
        op.create_unique_constraint('channel_amqp_uq1', model.ChannelAMQP.__tablename__, ['name', 'def_id'])
        op.create_unique_constraint('out_amqp_uq1', model.OutgoingAMQP.__tablename__, ['name', 'def_id'])

def downgrade():
    pass

"""gh40 add STOMP

Revision ID: 0030_8261ae81b
Revises: 0029_7e71a8117
Create Date: 2015-02-24 08:50:23
"""

revision = '0030_8261ae81b'
down_revision = '0029_7e71a8117'

from alembic import op
import sqlalchemy as sa

# Zato
from zato.common import STOMP
from zato.common.odb import model

# ################################################################################################################################

def upgrade():

    # Outgoing connection

    op.execute(CreateSequence(sa.Sequence('out_stomp_seq')))
    op.create_table(
        model.OutgoingSTOMP.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('out_stomp_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),

        sa.Column('username', sa.String(200), nullable=True, default=STOMP.DEFAULT.USERNAME),
        sa.Column('password', sa.String(200), nullable=True),

        sa.Column('address', sa.String(200), nullable=False, default=STOMP.DEFAULT.ADDRESS),
        sa.Column('proto_version', sa.String(20), nullable=False, default=STOMP.DEFAULT.PROTOCOL),
        sa.Column('timeout', sa.Integer(), nullable=False, default=STOMP.DEFAULT.TIMEOUT),

        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        )
    op.create_unique_constraint(
        'out_stomp_seq_name_cluster_id_key', model.OutgoingSTOMP.__tablename__, ['name', 'cluster_id']
        )

    # Channel

    op.execute(CreateSequence(sa.Sequence('channel_seq')))
    op.create_table(
        model.OutgoingSTOMP.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('channel_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),

        sa.Column('username', sa.String(200), nullable=True, default=STOMP.DEFAULT.USERNAME),
        sa.Column('password', sa.String(200), nullable=True),

        sa.Column('address', sa.String(200), nullable=False, default=STOMP.DEFAULT.ADDRESS),
        sa.Column('proto_version', sa.String(20), nullable=False, default=STOMP.DEFAULT.PROTOCOL),
        sa.Column('timeout', sa.Integer(), nullable=False, default=STOMP.DEFAULT.TIMEOUT),
        sa.Column('sub_to', sa.Text(), nullable=False),

        sa.Column('service_id', sa.Integer(), sa.ForeignKey('service.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        )
    op.create_unique_constraint(
        'channel_seq_name_cluster_id_key', model.OutgoingSTOMP.__tablename__, ['name', 'cluster_id']
        )

def downgrade():
    op.drop_table(model.OutgoingSTOMP.__tablename__)
    op.drop_table(model.ChannelSTOMP.__tablename__)

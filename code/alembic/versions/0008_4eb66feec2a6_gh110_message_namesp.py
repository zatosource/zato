"""gh110 Message namespaces

Revision ID: 0008_4eb66feec2a6
Revises: 0007_c16781527a4
Create Date: 2013-11-22 13:34:36.678790

"""

# revision identifiers, used by Alembic.
revision = '0008_4eb66feec2a6'
down_revision = '0007_c16781527a4'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'msg_ns',
        sa.Column('id', sa.Integer, sa.Sequence('msg_ns_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('value', sa.String(500), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
    )
    op.create_unique_constraint(None, 'msg_ns', ['name', 'cluster_id'])

def downgrade():
    op.drop_table('msg_ns')

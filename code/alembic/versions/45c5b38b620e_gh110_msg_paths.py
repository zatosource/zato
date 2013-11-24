"""gh110 Msg paths

Revision ID: 45c5b38b620e
Revises: 4eb66feec2a6
Create Date: 2013-11-24 17:05:50.526032

"""

# revision identifiers, used by Alembic.
revision = '45c5b38b620e'
down_revision = '4eb66feec2a6'

from alembic import op
import sqlalchemy as sa

# Zato
from zato.common.odb import model

def upgrade():
    op.create_table(
        'msg_xpath',
        sa.Column('id', sa.Integer, sa.Sequence('msg_xpath_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False, index=True),
        sa.Column('value', sa.String(500), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
    )

    op.create_table(
        'msg_elem_path',
        sa.Column('id', sa.Integer, sa.Sequence('msg_elem_path_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False, index=True),
        sa.Column('value', sa.String(500), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
    )

    op.create_unique_constraint(None, 'msg_xpath', ['name', 'cluster_id'])
    op.create_unique_constraint(None, 'msg_elem_path', ['name', 'cluster_id'])

def downgrade():
    op.drop_table('msg_xpath')
    op.drop_table('msg_elem_path')

"""gh229 Msg paths

Revision ID: 0009_45c5b38b620e
Revises: 0008_4eb66feec2a6
Create Date: 2013-11-24 17:05:50.526032

"""

# revision identifiers, used by Alembic.
revision = '0009_45c5b38b620e'
down_revision = '0008_4eb66feec2a6'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence, DropSequence

# Zato
from zato.common.odb import model

# ################################################################################################################################

def upgrade():
    op.execute(CreateSequence(sa.Sequence('msg_xpath_seq')))
    op.create_table(
        model.XPath.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('msg_xpath_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('value', sa.String(1500), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        sa.UniqueConstraint('name','cluster_id')
        )

    op.execute(CreateSequence(sa.Sequence('msg_json_pointer_seq')))
    op.create_table(
        model.JSONPointer.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('msg_json_pointer_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('value', sa.String(1500), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        sa.UniqueConstraint('name', 'cluster_id')
        )

def downgrade():
    op.drop_table(model.XPath.__tablename__)
    op.execute(DropSequence(sa.Sequence('msg_xpath_seq')))
    op.drop_table(model.JSONPointer.__tablename__)
    op.execute(DropSequence(sa.Sequence('msg_json_pointer_seq')))

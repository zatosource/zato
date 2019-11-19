"""gh105 Odoo

Revision ID: 0025_3e918a21
Revises: 0024_93a91735
Create Date: 2014-10-22 17:03:13

"""

# Revision identifiers, used by Alembic.
revision = '0025_3e918a21'
down_revision = '0024_93a91735'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence

# Zato
from zato.common import ODOO
from zato.common.odb import model

# ################################################################################################################################

def upgrade():

    op.execute(CreateSequence(sa.Sequence('out_odoo_seq')))
    op.create_table(
        model.OutgoingOdoo.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('out_odoo_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('host', sa.String(200), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False, default=ODOO.DEFAULT.PORT),
        sa.Column('user', sa.String(200), nullable=False),
        sa.Column('database', sa.String(200), nullable=False),
        sa.Column('protocol', sa.String(200), nullable=False),
        sa.Column('pool_size', sa.Integer(), nullable=False),
        sa.Column('password', sa.String(400), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        )
    op.create_unique_constraint(
        'out_odoo_seq_name_cluster_id_key', model.OutgoingOdoo.__tablename__, ['name', 'cluster_id']
        )

def downgrade():
    op.drop_table(model.OutgoingOdoo.__tablename__)

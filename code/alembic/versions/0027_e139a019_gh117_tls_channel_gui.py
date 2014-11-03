"""gh117 TLS channel GUI

Revision ID: 0027_e139a019
Revises: 0026_7aa19137
Create Date: 2014-11-03 19:31:51

"""

# revision identifiers, used by Alembic.
revision = '0027_e139a019'
down_revision = '0026_7aa19137'

from alembic import op
import sqlalchemy as sa

# Zato
from zato.common.odb import model

def upgrade():
    op.create_table(model.TLSChannelSecurity.__tablename__,
        sa.Column('id', sa.Integer(), sa.ForeignKey('sec_base.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('value', sa.LargeBinary(200000), nullable=False))

def downgrade():
    op.drop_table(model.TLSChannelSecurity.__tablename__)

"""gh118 TLS outconns

Revision ID: 0015_f67f3ea1
Revises: 0014_50465d9c19e0
Create Date: 2014-07-05 20:53:05

"""

# revision identifiers, used by Alembic.
revision = '0015_f67f3ea1'
down_revision = '0014_50465d9c19e0'

from alembic import op
import sqlalchemy as sa

# Zato
from zato.common.odb import model

def upgrade():
    op.create_table(model.TLSKeyCertSecurity.__tablename__,
        sa.Column('id', sa.Integer(), sa.ForeignKey('sec_base.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('fs_name', sa.String(200), nullable=False),
        sa.Column('cert_fp', sa.String(200), nullable=False),
        sa.Column('cert_cn', sa.String(1200), nullable=False))

def downgrade():
    op.drop_table(model.TLSKeyCertSecurity.__tablename__)

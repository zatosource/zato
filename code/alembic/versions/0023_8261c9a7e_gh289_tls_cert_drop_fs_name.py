"""gh289

Revision ID: 0023_8261c9a7e
Revises: 0022_a78ac9178
Create Date: 2014-10-09 07:20:32

"""
revision = '0023_8261c9a7e'
down_revision = '0022_a78ac9178'

from alembic import op
import sqlalchemy as sa

# Zato
from zato.common.odb import model

# ################################################################################################################################

def upgrade():
    op.drop_column(model.TLSCACert.__tablename__, 'fs_name')
    op.add_column(model.TLSCACert.__tablename__, sa.Column('value', sa.LargeBinary(200000), nullable=False))
    op.add_column(model.TLSCACert.__tablename__, sa.Column('info', sa.LargeBinary(200000), nullable=False))

def downgrade():
    op.add_column(model.TLSCACert.__tablename__, sa.Column('fs_name', sa.String(200), nullable=False))
    op.drop_column(model.TLSCACert.__tablename__, 'value')
    op.drop_column(model.TLSCACert.__tablename__, 'info')

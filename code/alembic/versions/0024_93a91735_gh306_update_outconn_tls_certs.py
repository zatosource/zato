"""gh306

Revision ID: 0024_93a91735
Revises: 0023_8261c9a7e
Create Date: 2014-10-14 18:37:47

"""
revision = '0024_93a91735'
down_revision = '0023_8261c9a7e'

from alembic import op

# Zato
from zato.common.odb import model

# ################################################################################################################################

def upgrade():
    op.drop_column(model.TLSCACert.__tablename__, 'fs_name')
    op.drop_column(model.TLSCACert.__tablename__, 'cert_fp')
    op.drop_column(model.TLSCACert.__tablename__, 'cert_subject')
    op.add_column(model.TLSCACert.__tablename__, sa.Column('info', sa.LargeBinary(200000), nullable=False))
    op.add_column(model.TLSCACert.__tablename__, sa.Column('value', sa.LargeBinary(200000), nullable=False))

def downgrade():
    op.add_column(model.TLSCACert.__tablename__, sa.Column('fs_name', sa.String(200), nullable=False))
    op.add_column(model.TLSCACert.__tablename__, sa.Column('cert_fp', sa.String(200), nullable=False))
    op.add_column(model.TLSCACert.__tablename__, sa.Column('cert_subject', sa.String(1200), nullable=False))
    op.drop_column(model.TLSCACert.__tablename__, 'info')
    op.drop_column(model.TLSCACert.__tablename__, 'value')

"""gh283 update tls outconns

Revision ID: 0017_7baa0602
Revises: 0016_6669bb02
Create Date: 2014-07-18 14:47:05

"""

# revision identifiers, used by Alembic.
revision = '0017_7baa0602'
down_revision = '0016_6669bb02'

from alembic import op
import sqlalchemy as sa

# Zato
from zato.common.odb import model

# ################################################################################################################################

def upgrade():
    op.drop_column(model.TLSKeyCertSecurity.__tablename__, 'cert_cn')    
    op.add_column(model.TLSKeyCertSecurity.__tablename__, sa.Column('cert_subject', sa.String(1200), nullable=False))
    
    op.drop_constraint('sec_tls_key_cert_id_fkey', model.TLSKeyCertSecurity.__tablename__)
    op.create_foreign_key('sec_tls_key_cert_id_fkey', model.TLSKeyCertSecurity.__tablename__, 'sec_base', ['id'], ['id'])
    
def downgrade():
    op.drop_column(model.TLSKeyCertSecurity.__tablename__, 'cert_subject')    
    op.add_column(model.TLSKeyCertSecurity.__tablename__, sa.Column('cert_cn', sa.String(1200), nullable=False))

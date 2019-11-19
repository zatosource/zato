"""gh283 update tls outconns

Revision ID: 0029_7e71a8117
Revises: 0028_ae3419a9
Create Date: 2015-01-21 16:23:14

"""

# revision identifiers, used by Alembic.
revision = '0029_7e71a8117'
down_revision = '0028_ae3419a9'

from alembic import op
import sqlalchemy as sa

# Zato
from zato.common.odb import model

# ################################################################################################################################

def upgrade():
    op.drop_column(model.TLSKeyCertSecurity.__tablename__, 'cert_subject')
    op.add_column(model.TLSKeyCertSecurity.__tablename__, sa.Column('info', sa.LargeBinary(200000), nullable=False))
    op.add_column(model.TLSKeyCertSecurity.__tablename__, sa.Column('value', sa.LargeBinary(200000), nullable=False))

def downgrade():
    op.drop_column(model.TLSKeyCertSecurity.__tablename__, 'info')
    op.drop_column(model.TLSKeyCertSecurity.__tablename__, 'value')
    op.add_column(model.TLSKeyCertSecurity.__tablename__, sa.Column('cert_subject', sa.String(1200), nullable=False))

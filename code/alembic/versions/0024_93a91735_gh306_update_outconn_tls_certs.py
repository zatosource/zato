"""gh306

Revision ID: 0024_93a91735
Revises: 0023_8261c9a7e
Create Date: 2014-10-14 18:37:47

"""
revision = '0024_93a91735'
down_revision = '0023_8261c9a7e'

from alembic import op
import sqlalchemy as sa

# Zato
from zato.common.odb import model

# ################################################################################################################################

def upgrade():
    pass

def downgrade():
    pass

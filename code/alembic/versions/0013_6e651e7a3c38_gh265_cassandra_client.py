"""gh265 Cassandra client

Revision ID: 0013_6e651e7a3c38
Revises: 0012_c70a22206a1
Create Date: 2014-06-26 00:44:32

"""

# revision identifiers, used by Alembic.
revision = '0013_6e651e7a3c38'
down_revision = '0012_c70a22206a1'

from alembic import op
import sqlalchemy as sa

# Zato
from zato.common.odb import model

def upgrade():
    pass

def downgrade():
    pass
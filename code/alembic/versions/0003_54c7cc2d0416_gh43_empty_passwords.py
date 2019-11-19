"""gh43: Empty passwords in sec definitions

Revision ID: 0003_54c7cc2d0416
Revises: 0002_3dfa60e5b541
Create Date: 2013-10-29 21:28:49.103205

"""

# revision identifiers, used by Alembic.
revision = '0003_54c7cc2d0416'
down_revision = '0002_3dfa60e5b541'

from alembic import op

# Zato
from zato.common.odb import model


def upgrade():
    op.alter_column(model.SecurityBase.__tablename__, 'password', nullable=True)

def downgrade():
    op.alter_column(model.SecurityBase.__tablename__, 'password', nullable=False)

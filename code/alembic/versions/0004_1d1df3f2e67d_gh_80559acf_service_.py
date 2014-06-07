"""gh 80559acf Service.name (300)

Revision ID: 0004_1d1df3f2e67d
Revises: 0003_54c7cc2d0416
Create Date: 2013-10-29 22:18:59.663205

"""

# revision identifiers, used by Alembic.
revision = '0004_1d1df3f2e67d'
down_revision = '0003_54c7cc2d0416'

from alembic import op
import sqlalchemy as sa

# Zato
from zato.common.odb import model

def upgrade():
    op.alter_column(model.Service.__tablename__, 'name',
        type_=sa.String(300), existing_type=sa.String(length=2000),
        nullable=False)


def downgrade():
    op.alter_column(model.Service.__tablename__, 'name',
        type_=sa.String(2000), existing_type=sa.String(length=300),
        nullable=False)

"""gh236 Async Postgres driver pg8000

Revision ID: 0012_c70a22206a1
Revises: 0011_1500abb1cf3
Create Date: 2014-05-25 10:38:01

"""

# revision identifiers, used by Alembic.
revision = '0012_c70a22206a1'
down_revision = '0011_1500abb1cf3'


from alembic import op
from sqlalchemy.sql import table as _table, column
from sqlalchemy import String

# Zato
from zato.common.odb import model

table = _table(model.SQLConnectionPool.__tablename__, column('engine', String))

def _operation(from_, to):
    op.execute(
        table.update().where(
            table.c.engine==op.inline_literal(from_)).values({'engine':op.inline_literal(to)}))

def upgrade():
    _operation('postgresql', 'postgresql+pg8000')

def downgrade():
    _operation('postgresql+pg8000', 'postgresql')

"""gh77: Outconn HTTP/SOAP pool size

Revision ID: 0002_3dfa60e5b541
Revises: 0001_419059182a1d
Create Date: 2013-10-29 21:14:14.310464

"""

# revision identifiers, used by Alembic.
revision = '0002_3dfa60e5b541'
down_revision = '0001_419059182a1d'

from alembic import op
import sqlalchemy as sa

# Zato
from zato.common.odb import model


def upgrade():
    op.add_column(model.HTTPSOAP.__tablename__,
        sa.Column('pool_size', sa.Integer, nullable=True)
    )


def downgrade():
    op.drop_column('http_soap', 'pool_size')

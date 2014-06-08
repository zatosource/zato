"""gh44: Pinging Plain HTTP outgoing connection

Revision ID: 0001_419059182a1d
Revises: None
Create Date: 2013-10-29 20:27:14.040498

"""

# revision identifiers, used by Alembic.
revision = '0001_419059182a1d'
down_revision = None

from alembic import op
import sqlalchemy as sa

# Zato
from zato.common.odb import model

def upgrade():
    op.add_column(model.HTTPSOAP.__tablename__,
        sa.Column('ping_method', sa.String(60), nullable=True)
    )

def downgrade():
    op.drop_column('http_soap', 'ping_method')

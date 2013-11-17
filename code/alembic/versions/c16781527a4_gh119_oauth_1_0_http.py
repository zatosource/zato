"""gh119: OAuth 1.0 HTTP channels

Revision ID: c16781527a4
Revises: 2538d53b16c8
Create Date: 2013-11-13 14:57:36.541735

"""

# revision identifiers, used by Alembic.
revision = 'c16781527a4'
down_revision = '2538d53b16c8'

from alembic import op
import sqlalchemy as sa

# Zato
from zato.common.odb import model

def upgrade():
    op.create_table(
        'sec_oauth',
        sa.Column('id', sa.Integer, sa.ForeignKey('sec_base.id'), primary_key=True),
        sa.Column('username', sa.String(32), nullable=False),
        sa.Column('proto_version', sa.String(32), nullable=False),
        sa.Column('sig_method', sa.String(32), nullable=False),
        sa.Column('max_nonce_log', sa.Integer(), nullable=False),
    )

def downgrade():
    op.drop_table('sec_oauth')

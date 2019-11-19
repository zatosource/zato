"""gh119: OAuth 1.0 HTTP channels

Revision ID: 0007_c16781527a4
Revises: 0006_2538d53b16c8
Create Date: 2013-11-13 14:57:36.541735

"""

# revision identifiers, used by Alembic.
revision = '0007_c16781527a4'
down_revision = '0006_2538d53b16c8'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'sec_oauth',
        sa.Column('id', sa.Integer, sa.ForeignKey('sec_base.id'), primary_key=True),
        sa.Column('proto_version', sa.String(32), nullable=False),
        sa.Column('sig_method', sa.String(32), nullable=False),
        sa.Column('max_nonce_log', sa.Integer(), nullable=False),
    )

def downgrade():
    op.drop_table('sec_oauth')

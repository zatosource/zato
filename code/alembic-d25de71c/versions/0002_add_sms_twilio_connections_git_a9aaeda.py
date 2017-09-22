"""Add SMS Twilio connections.

Revision ID: 0002_add_sms_twilio_connections_git_a9aaeda
Revises: 0001_194dfa_git_25de71c
Create Date: 2017-09-02 18:07:09.377901

"""

# revision identifiers, used by Alembic.
revision = '0002_add_sms_twilio_connections_git_a9aaeda'
down_revision = '0001_194dfa_git_25de71c'

from alembic import context, op
import sqlalchemy as sa

# Zato
from zato.common.odb import model

def is_sqlite():
    config = context.config.get_section('alembic')
    return 'sqlite' in config.get('sqlalchemy.url').lower()

def upgrade():

    op.create_table(
        model.SMSTwilio.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('sms_twilio_id_seq'), nullable=False, primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_internal', sa.Boolean(), nullable=False, default=False),

        sa.Column('account_sid', sa.String(200), nullable=False),
        sa.Column('auth_token', sa.String(200), nullable=False),

        sa.Column('default_from', sa.String(200), nullable=True),
        sa.Column('default_to', sa.String(200), nullable=True),

        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', name='sms_twilio_cluster_id_fkey', ondelete='CASCADE'),
            nullable=False),
        )

    # SQLite doesn't support these operations

    if not is_sqlite():
        op.create_unique_constraint('sms_twilio_uq1', model.SMSTwilio.__tablename__, ['name', 'cluster_id'])


def downgrade():
    op.drop_table(model.SMSTwilio.__tablename__)

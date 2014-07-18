"""gh284 smtp

Revision ID: 0018_ed18fc6a
Revises: 0017_7baa0602
Create Date: 2014-07-18 15:07:05

"""

# revision identifiers, used by Alembic.
revision = '0018_ed18fc6a'
down_revision = '0017_7baa0602'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence, DropSequence

# Zato
from zato.common.odb import model

# ################################################################################################################################

def upgrade():
    op.execute(CreateSequence(sa.Sequence('email_smtp_seq')))
    
    op.create_table(
        model.SMTP.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('email_smtp_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('host', sa.String(400), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False),
        sa.Column('timeout', sa.Integer(), nullable=False),
        sa.Column('is_debug', sa.Boolean(), nullable=False),
        sa.Column('username', sa.String(400), nullable=True),
        sa.Column('password', sa.String(400), nullable=True),
        sa.Column('mode', sa.String(20), nullable=False),
        sa.Column('ping_address', sa.String(200), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        )        
    op.create_unique_constraint(
        'email_smtp_name_cluster_id_key', model.SMTP.__tablename__, ['name', 'cluster_id']
        )    

def downgrade():
    op.drop_table(model.SMTP.__tablename__)
    op.execute(DropSequence(sa.Sequence('email_smtp_seq')))

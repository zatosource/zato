"""gh290 sql notifications

Revision ID: 0020_bf41328c
Revises: 0019_e77a8c06
Create Date: 2014-07-24 20:05:05

"""

# revision identifiers, used by Alembic.
revision = '0020_bf41328c'
down_revision = '0019_e77a8c06'

from alembic import op
import sqlalchemy as sa

# Zato
from zato.common.odb import model

# ################################################################################################################################
    
def upgrade():   
    op.create_table(
        model.NotificationSQL.__tablename__,
        sa.Column('id', sa.Integer(), sa.ForeignKey('notif.id'), primary_key=True),
        sa.Column('query', sa.String(200000), nullable=False),
        sa.Column('def_id', sa.Integer(), sa.ForeignKey('sql_pool.id'), primary_key=True),
        )
        
    op.alter_column(model.Notification.__tablename__, 'name_pattern', nullable=True)
    op.alter_column(model.Notification.__tablename__, 'name_pattern_neg', nullable=True)
    op.alter_column(model.Notification.__tablename__, 'get_data', nullable=True)
    op.alter_column(model.Notification.__tablename__, 'get_data_patt', nullable=True)
    op.alter_column(model.Notification.__tablename__, 'get_data_patt_neg', nullable=True)
            
def downgrade():
    op.drop_table(model.NotificationSQL.__tablename__)
    op.alter_column(model.Notification.__tablename__, 'name_pattern', nullable=False)
    op.alter_column(model.Notification.__tablename__, 'name_pattern_neg', nullable=False)
    op.alter_column(model.Notification.__tablename__, 'get_data', nullable=False)
    op.alter_column(model.Notification.__tablename__, 'get_data_patt', nullable=False)
    op.alter_column(model.Notification.__tablename__, 'get_data_patt_neg', nullable=False)

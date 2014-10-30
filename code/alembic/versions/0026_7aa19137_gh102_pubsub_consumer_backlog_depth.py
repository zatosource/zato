"""gh102 Rename pub_sub_consumer.max_backlog to pub_sub_consumer.max_depth

Revision ID: 0026_7aa19137
Revises: 0025_3e918a21
Create Date: 2014-10-28 18:58:00

"""

# Revision identifiers, used by Alembic.
revision = '0026_7aa19137'
down_revision = '0025_3e918a21'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence

# Zato
from zato.common.odb import model

# ################################################################################################################################

def upgrade():
    op.add_column(model.PubSubConsumer.__tablename__, sa.Column('max_depth', sa.Integer, nullable=False))
    op.drop_column(model.PubSubConsumer.__tablename__, 'max_backlog')

def downgrade():
    op.add_column(model.PubSubConsumer.__tablename__, sa.Column('max_backlog', sa.Integer, nullable=False))
    op.drop_column(model.PubSubConsumer.__tablename__, 'max_depth')
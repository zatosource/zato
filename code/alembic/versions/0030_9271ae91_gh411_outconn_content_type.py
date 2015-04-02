"""gh411 content_type in outgoing connections

Revision ID: 0030_9271ae91
Revises: 0029_7e71a8117
Create Date: 2015-04-02 16:51:18

"""

# revision identifiers, used by Alembic.
revision = '0030_9271ae91'
down_revision = '0029_7e71a8117'

from alembic import op
import sqlalchemy as sa

# Zato
from zato.common.odb import model

# ################################################################################################################################

def upgrade():
    op.add_column(model.HTTPSOAP.__tablename__, sa.Column('content_type', sa.String(200), nullable=True))

def downgrade():
    op.drop_column(model.HTTPSOAP.__tablename__, 'content_type')

"""gh307-rbac

Revision ID: 0022_a78ac9178
Revises: 0021_d9e54066
Create Date: 2014-09-16 13:06:01

"""
revision = '0022_a78ac9178'
down_revision = '0021_d9e54066'

from alembic import op

# Zato
from zato.common.odb import model

# ################################################################################################################################

def upgrade():
    op.alter_column(model.RBACRole.__tablename__, 'parent_id', nullable=True)

def downgrade():
    op.alter_column(model.RBACRole.__tablename__, 'parent_id', nullable=False)

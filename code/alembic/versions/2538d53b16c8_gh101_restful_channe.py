"""gh101 RESTful channels (URL params + priority)

Revision ID: 2538d53b16c8
Revises: 15a75c65a3a1
Create Date: 2013-10-29 23:37:49.556055

"""

# revision identifiers, used by Alembic.
revision = '2538d53b16c8'
down_revision = '15a75c65a3a1'

from alembic import op
import sqlalchemy as sa

# Zato
from zato.common.odb import model

def upgrade():
    op.add_column(model.HTTPSOAP.__tablename__,
        sa.Column('merge_url_params_req', sa.Boolean, nullable=True, default=True))
    
    op.add_column(model.HTTPSOAP.__tablename__,
        sa.Column('url_params_pri', sa.String(200), nullable=True, default='path-then-qs'))

    op.add_column(model.HTTPSOAP.__tablename__,
        sa.Column('params_pri', sa.String(200), nullable=True, default='url-then-msg'))

def downgrade():
    op.drop_column('http_soap', 'merge_url_params_req')
    op.drop_column('http_soap', 'url_params_pri')
    op.drop_column('http_soap', 'params_pri')

"""gh110 HTTP channels audit

Revision ID: 0010_3f03ae0ef253
Revises: 0009_45c5b38b620e
Create Date: 2013-11-27 20:54:35.653604

"""

# revision identifiers, used by Alembic.
revision = '0010_3f03ae0ef253'
down_revision = '0009_45c5b38b620e'

from alembic import op
import sqlalchemy as sa

# Zato
from zato.common.util import alter_column_nullable_false
from zato.common import MISC, MSG_PATTERN_TYPE
from zato.common.odb import model

add_col = op.add_column

def upgrade():

    add_col(
        model.HTTPSOAP.__tablename__, sa.Column('audit_enabled', sa.Boolean(), nullable=True))
    alter_column_nullable_false(
        model.HTTPSOAP.__tablename__, 'audit_enabled', False, sa.Boolean())    

    add_col(
        model.HTTPSOAP.__tablename__, sa.Column('audit_back_log', sa.Integer(), nullable=True))
    alter_column_nullable_false(
        model.HTTPSOAP.__tablename__, 'audit_back_log', MISC.DEFAULT_AUDIT_BACK_LOG, sa.Integer())

    add_col(
        model.HTTPSOAP.__tablename__, sa.Column(
            'audit_max_payload', sa.Integer(), nullable=True, default=MISC.DEFAULT_AUDIT_MAX_PAYLOAD))
    alter_column_nullable_false(
        model.HTTPSOAP.__tablename__,'audit_max_payload', MISC.DEFAULT_AUDIT_MAX_PAYLOAD, sa.Integer())

    add_col(
        model.HTTPSOAP.__tablename__, sa.Column('audit_repl_patt_type', sa.String(200), nullable=True))
    alter_column_nullable_false(
        model.HTTPSOAP.__tablename__, 'audit_repl_patt_type', MSG_PATTERN_TYPE.JSON_POINTER.id, sa.String(200))
    
def downgrade():
    op.drop_column(model.HTTPSOAP.__tablename__, 'audit_enabled')
    op.drop_column(model.HTTPSOAP.__tablename__, 'audit_back_log')
    op.drop_column(model.HTTPSOAP.__tablename__, 'audit_max_payload')
    op.drop_column(model.HTTPSOAP.__tablename__, 'audit_repl_patt_type')

"""gh298-rbac

Revision ID: 0021_d9e54066
Revises: 0020_bf41328c
Create Date: 2014-08-28 10:48:05

"""

# revision identifiers, used by Alembic.
revision = '0021_d9e54066'
down_revision = '0020_bf41328c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence, DropSequence

# Zato
from zato.common.odb import model
from zato.common.util import alter_column_nullable_false

# ################################################################################################################################

def upgrade():

    op.add_column(
        model.HTTPSOAP.__tablename__, sa.Column('has_rbac', sa.Boolean(), nullable=True))
    alter_column_nullable_false(
        model.HTTPSOAP.__tablename__, 'has_rbac', False, sa.Boolean())

    op.execute(CreateSequence(sa.Sequence('rbac_role_seq')))
    op.create_table(
        model.RBACRole.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('rbac_cli_rol_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('rbac_role.id', ondelete='CASCADE')),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        )
    op.create_unique_constraint(
        'rbac_role_name_cluster_id_key', model.RBACRole.__tablename__, ['name', 'cluster_id']
        )

    op.execute(CreateSequence(sa.Sequence('rbac_cli_rol_seq')))
    op.create_table(
        model.RBACClientRole.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('rbac_cli_rol_seq'), primary_key=True),
        sa.Column('name', sa.String(400), nullable=False),
        sa.Column('client_def', sa.String(200), nullable=False),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('rbac_role.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        )
    op.create_unique_constraint(
        'rbac_client_role_client_def_role_id_cluster_id_key', model.RBACClientRole.__tablename__,\
        ['client_def', 'role_id', 'cluster_id']
        )

    op.execute(CreateSequence(sa.Sequence('rbac_perm_seq')))
    op.create_table(
        model.RBACPermission.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('rbac_cli_rol_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        )
    op.create_unique_constraint(
        'rbac_perm_name_cluster_id_key', model.RBACPermission.__tablename__, ['name', 'cluster_id']
        )

    op.execute(CreateSequence(sa.Sequence('rbac_role_perm_seq')))
    op.create_table(
        model.RBACRolePermission.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('rbac_cli_rol_seq'), primary_key=True),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('rbac_role.id', ondelete='CASCADE'), nullable=False),
        sa.Column('perm_id', sa.Integer(), sa.ForeignKey('rbac_perm.id', ondelete='CASCADE'), nullable=False),
        sa.Column('service_id', sa.Integer(), sa.ForeignKey('service.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        )
    op.create_unique_constraint(
        'rbac_role_perm_role_id_perm_id_service_id_cluster_id_key', model.RBACRolePermission.__tablename__,\
        ['role_id', 'perm_id', 'service_id', 'cluster_id']
        )

def downgrade():
    op.execute(DropSequence(sa.Sequence('rbac_cli_rol_seq')))
    op.execute(DropSequence(sa.Sequence('rbac_perm_seq')))
    op.execute(DropSequence(sa.Sequence('rbac_role_perm_seq')))
    op.drop_column(model.HTTPSOAP.__tablename__, 'has_rbac')
    op.execute(DropSequence(sa.Sequence('rbac_role_seq')))
    op.drop_table(model.RBACRolePermission.__tablename__)
    op.drop_table(model.RBACClientRole.__tablename__)
    op.drop_table(model.RBACRole.__tablename__)
    op.drop_table(model.RBACPermission.__tablename__)

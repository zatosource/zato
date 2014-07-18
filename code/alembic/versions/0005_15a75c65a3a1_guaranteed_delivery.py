"""Guaranteed delivery

Revision ID: 0005_15a75c65a3a1
Revises: 0004_1d1df3f2e67d
Create Date: 2013-10-29 22:26:17.288183

"""

# revision identifiers, used by Alembic.
revision = '0005_15a75c65a3a1'
down_revision = '0004_1d1df3f2e67d'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'delivery_def_base',
        sa.Column('id', sa.Integer, sa.Sequence('deliv_def_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False, index=True),
        sa.Column('short_def', sa.String(200), nullable=False),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('target_type', sa.String(200), nullable=False),
        sa.Column('callback_list', sa.LargeBinary(10000), nullable=True),
        sa.Column('expire_after', sa.Integer(), nullable=False),
        sa.Column('expire_arch_succ_after', sa.Integer(), nullable=False),
        sa.Column('expire_arch_fail_after', sa.Integer(), nullable=False),
        sa.Column('check_after', sa.Integer(), nullable=False),
        sa.Column('retry_repeats', sa.Integer(), nullable=False),
        sa.Column('retry_seconds', sa.Integer(), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
    )
    
    op.create_table(
        'delivery_def_out_wmq',
        sa.Column('id', sa.Integer, sa.ForeignKey('delivery_def_base.id'), primary_key=True),
        sa.Column('target_id', sa.Integer, sa.ForeignKey('out_wmq.id', ondelete='CASCADE'), nullable=False, primary_key=False)
    )
    
    op.create_table(
        'delivery',
        sa.Column('id', sa.Integer, sa.Sequence('deliv_seq'), primary_key=True),
        sa.Column('task_id', sa.String(64), unique=True, nullable=False, index=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('creation_time', sa.DateTime(), nullable=False),
        sa.Column('args', sa.LargeBinary(1000000), nullable=True),
        sa.Column('kwargs', sa.LargeBinary(1000000), nullable=True),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('resubmit_count', sa.Integer, nullable=False, default=0),
        sa.Column('state', sa.String(200), nullable=False, index=True),
        sa.Column('source_count', sa.Integer, nullable=False, default=1),
        sa.Column('target_count', sa.Integer, nullable=False, default=0),
        sa.Column('definition_id', sa.Integer, sa.ForeignKey('delivery_def_base.id', ondelete='CASCADE'), nullable=False, primary_key=False),
    )

    op.create_table(
        'delivery_payload',
        sa.Column('id', sa.Integer, sa.Sequence('deliv_payl_seq'), primary_key=True),
        sa.Column('task_id', sa.String(64), nullable=False, unique=True, index=True),
        sa.Column('creation_time', sa.DateTime(), nullable=False),
        sa.Column('payload', sa.LargeBinary(5000000), nullable=False),
        sa.Column('delivery_id', sa.Integer, sa.ForeignKey('delivery.id', ondelete='CASCADE'), nullable=False, primary_key=False),
    )
    
    op.create_table(
        'delivery_history',
        sa.Column('id', sa.Integer, sa.Sequence('deliv_payl_seq'), primary_key=True),
        sa.Column('task_id', sa.String(64), nullable=False, unique=True, index=True),
        sa.Column('entry_type', sa.String(64), nullable=False),
        sa.Column('entry_time', sa.DateTime(), nullable=False, index=True),
        sa.Column('entry_ctx', sa.LargeBinary(6000000), nullable=False),
        sa.Column('resubmit_count', sa.Integer, nullable=False, default=0),
        sa.Column('delivery_id', sa.Integer, sa.ForeignKey('delivery.id', ondelete='CASCADE'), nullable=False, primary_key=False),
    )

def downgrade():
    op.drop_table('delivery_history')
    op.drop_table('delivery_payload')
    op.drop_table('delivery')
    op.drop_table('delivery_def_out_wmq')
    op.drop_table('delivery_def_base')

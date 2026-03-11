"""Add WorkLog settlement system tables

Revision ID: f1a2b3c4d5e6
Revises: 1a31ce608336
Create Date: 2024-08-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


revision = 'f1a2b3c4d5e6'
down_revision = '1a31ce608336'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'worklog',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('task_id', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('remittance_status', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    
    op.create_table(
        'timesegment',
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('worklog_id', sa.UUID(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['worklog_id'], ['worklog.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    
    op.create_table(
        'remittance',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('remittance_date', sa.DateTime(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('worklog_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['worklog_id'], ['worklog.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    
    op.create_table(
        'adjustment',
        sa.Column('worklog_id', sa.UUID(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('reason', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['worklog_id'], ['worklog.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('adjustment')
    op.drop_table('remittance')
    op.drop_table('timesegment')
    op.drop_table('worklog')

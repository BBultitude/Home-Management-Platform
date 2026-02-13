"""add_tax_wfh_and_travel_tables

Revision ID: 96b7cb77bf12
Revises: 95d85ef6ae4b
Create Date: 2026-02-12 00:08:10.056321

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96b7cb77bf12'
down_revision = '95d85ef6ae4b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tax_wfh_entries table
    op.create_table(
        'tax_wfh_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('hours', sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'date', name='uq_tax_wfh_user_date')
    )
    op.create_index('ix_tax_wfh_entries_id', 'tax_wfh_entries', ['id'])
    op.create_index('ix_tax_wfh_entries_user_id', 'tax_wfh_entries', ['user_id'])
    op.create_index('ix_tax_wfh_entries_date', 'tax_wfh_entries', ['date'])

    # Create tax_travel_entries table
    op.create_table(
        'tax_travel_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('purpose', sa.String(length=255), nullable=False),
        sa.Column('start_location', sa.String(length=255), nullable=False),
        sa.Column('end_location', sa.String(length=255), nullable=False),
        sa.Column('distance_km', sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tax_travel_entries_id', 'tax_travel_entries', ['id'])
    op.create_index('ix_tax_travel_entries_user_id', 'tax_travel_entries', ['user_id'])
    op.create_index('ix_tax_travel_entries_date', 'tax_travel_entries', ['date'])


def downgrade() -> None:
    # Drop indexes and tables
    op.drop_index('ix_tax_travel_entries_date', 'tax_travel_entries')
    op.drop_index('ix_tax_travel_entries_user_id', 'tax_travel_entries')
    op.drop_index('ix_tax_travel_entries_id', 'tax_travel_entries')
    op.drop_table('tax_travel_entries')

    op.drop_index('ix_tax_wfh_entries_date', 'tax_wfh_entries')
    op.drop_index('ix_tax_wfh_entries_user_id', 'tax_wfh_entries')
    op.drop_index('ix_tax_wfh_entries_id', 'tax_wfh_entries')
    op.drop_table('tax_wfh_entries')

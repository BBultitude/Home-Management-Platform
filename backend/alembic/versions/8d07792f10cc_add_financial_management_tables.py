"""add_financial_management_tables

Revision ID: 8d07792f10cc
Revises: 96b7cb77bf12
Create Date: 2026-02-13 15:38:09.787423

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d07792f10cc'
down_revision = '96b7cb77bf12'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE income_frequency AS ENUM ('daily', 'weekly', 'fortnightly', 'monthly', 'yearly')")
    op.execute("CREATE TYPE account_type AS ENUM ('checking', 'savings', 'offset')")
    op.execute("CREATE TYPE expense_frequency AS ENUM ('daily', 'weekly', 'fortnightly', 'monthly', 'yearly')")
    op.execute("CREATE TYPE utility_type AS ENUM ('electricity', 'gas', 'water', 'internet', 'mobile')")

    # Create income_sources table
    op.create_table(
        'income_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_name', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('frequency', sa.Enum('daily', 'weekly', 'fortnightly', 'monthly', 'yearly', name='income_frequency'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_income_sources_id'), 'income_sources', ['id'], unique=False)

    # Create bank_accounts table
    op.create_table(
        'bank_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_name', sa.String(length=255), nullable=False),
        sa.Column('account_type', sa.Enum('checking', 'savings', 'offset', name='account_type'), nullable=False),
        sa.Column('current_balance', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bank_accounts_id'), 'bank_accounts', ['id'], unique=False)

    # Create expense_categories table
    op.create_table(
        'expense_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_name', sa.String(length=255), nullable=False),
        sa.Column('bank_account_id', sa.Integer(), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['bank_account_id'], ['bank_accounts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_expense_categories_id'), 'expense_categories', ['id'], unique=False)
    op.create_index(op.f('ix_expense_categories_bank_account_id'), 'expense_categories', ['bank_account_id'], unique=False)

    # Create expenses table
    op.create_table(
        'expenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('expense_name', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('frequency', sa.Enum('daily', 'weekly', 'fortnightly', 'monthly', 'yearly', name='expense_frequency'), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['expense_categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_expenses_id'), 'expenses', ['id'], unique=False)
    op.create_index(op.f('ix_expenses_category_id'), 'expenses', ['category_id'], unique=False)

    # Create utilities table
    op.create_table(
        'utilities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('utility_type', sa.Enum('electricity', 'gas', 'water', 'internet', 'mobile', name='utility_type'), nullable=False),
        sa.Column('provider', sa.String(length=255), nullable=False),
        sa.Column('billing_period_start', sa.Date(), nullable=False),
        sa.Column('billing_period_end', sa.Date(), nullable=False),
        sa.Column('usage', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('cost', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('cost_per_unit', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('attachment_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['attachment_id'], ['files.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_utilities_id'), 'utilities', ['id'], unique=False)
    op.create_index(op.f('ix_utilities_utility_type'), 'utilities', ['utility_type'], unique=False)
    op.create_index(op.f('ix_utilities_billing_period_start'), 'utilities', ['billing_period_start'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_index(op.f('ix_utilities_billing_period_start'), table_name='utilities')
    op.drop_index(op.f('ix_utilities_utility_type'), table_name='utilities')
    op.drop_index(op.f('ix_utilities_id'), table_name='utilities')
    op.drop_table('utilities')

    op.drop_index(op.f('ix_expenses_category_id'), table_name='expenses')
    op.drop_index(op.f('ix_expenses_id'), table_name='expenses')
    op.drop_table('expenses')

    op.drop_index(op.f('ix_expense_categories_bank_account_id'), table_name='expense_categories')
    op.drop_index(op.f('ix_expense_categories_id'), table_name='expense_categories')
    op.drop_table('expense_categories')

    op.drop_index(op.f('ix_bank_accounts_id'), table_name='bank_accounts')
    op.drop_table('bank_accounts')

    op.drop_index(op.f('ix_income_sources_id'), table_name='income_sources')
    op.drop_table('income_sources')

    # Drop enum types
    op.execute("DROP TYPE utility_type")
    op.execute("DROP TYPE expense_frequency")
    op.execute("DROP TYPE account_type")
    op.execute("DROP TYPE income_frequency")

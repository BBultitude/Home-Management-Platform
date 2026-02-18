"""Consolidate: frequency options, nullable utilities, remove mobile/internet, add solar

Revision ID: update_util_solar
Revises: d8f42a1b9c3e
Create Date: 2026-02-18

Applies all pending changes:
1. Add bi_monthly, quarterly, semi_annually to income/expense frequency enums
2. Make utilities usage, unit, cost_per_unit nullable (for fixed-cost utilities like rates)
3. Remove 'mobile' and 'internet' from utility_type enum
4. Add solar_feed_in and solar_feed_in_credit columns to utilities
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_util_solar'
down_revision = 'd8f42a1b9c3e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -----------------------------------------------------------------------
    # 1. Add new frequency values to income_frequency and expense_frequency
    # -----------------------------------------------------------------------
    op.execute("ALTER TYPE income_frequency ADD VALUE IF NOT EXISTS 'bi_monthly'")
    op.execute("ALTER TYPE income_frequency ADD VALUE IF NOT EXISTS 'quarterly'")
    op.execute("ALTER TYPE income_frequency ADD VALUE IF NOT EXISTS 'semi_annually'")

    op.execute("ALTER TYPE expense_frequency ADD VALUE IF NOT EXISTS 'bi_monthly'")
    op.execute("ALTER TYPE expense_frequency ADD VALUE IF NOT EXISTS 'quarterly'")
    op.execute("ALTER TYPE expense_frequency ADD VALUE IF NOT EXISTS 'semi_annually'")

    # -----------------------------------------------------------------------
    # 2. Make utilities usage, unit, cost_per_unit nullable
    #    (allows fixed-cost utilities like council rates with no usage)
    # -----------------------------------------------------------------------
    op.alter_column('utilities', 'usage',
                    existing_type=sa.Numeric(precision=10, scale=2),
                    nullable=True)

    op.alter_column('utilities', 'unit',
                    existing_type=sa.String(length=50),
                    nullable=True)

    op.alter_column('utilities', 'cost_per_unit',
                    existing_type=sa.Numeric(precision=10, scale=4),
                    nullable=True)

    # -----------------------------------------------------------------------
    # 3. Remove 'mobile' and 'internet' from utility_type enum
    #    PostgreSQL requires recreating the enum to remove values
    # -----------------------------------------------------------------------
    # Delete any existing mobile/internet entries to avoid FK violations
    op.execute("DELETE FROM utilities WHERE utility_type IN ('mobile', 'internet')")

    # Rename old enum, create new one without mobile/internet
    op.execute("ALTER TYPE utility_type RENAME TO utility_type_old")
    op.execute("CREATE TYPE utility_type AS ENUM ('electricity', 'gas', 'water', 'rates')")

    # Cast column to new enum via text
    op.execute("""
        ALTER TABLE utilities
        ALTER COLUMN utility_type TYPE utility_type
        USING utility_type::text::utility_type
    """)

    # Drop the old enum
    op.execute("DROP TYPE utility_type_old")

    # -----------------------------------------------------------------------
    # 4. Add solar feed-in columns (electricity only, nullable)
    # -----------------------------------------------------------------------
    op.add_column('utilities', sa.Column('solar_feed_in', sa.Numeric(10, 2), nullable=True))
    op.add_column('utilities', sa.Column('solar_feed_in_credit', sa.Numeric(10, 2), nullable=True))


def downgrade() -> None:
    # Remove solar columns
    op.drop_column('utilities', 'solar_feed_in_credit')
    op.drop_column('utilities', 'solar_feed_in')

    # Restore utility_type enum with mobile/internet
    op.execute("ALTER TYPE utility_type RENAME TO utility_type_old")
    op.execute("CREATE TYPE utility_type AS ENUM ('electricity', 'gas', 'water', 'internet', 'mobile', 'rates')")
    op.execute("""
        ALTER TABLE utilities
        ALTER COLUMN utility_type TYPE utility_type
        USING utility_type::text::utility_type
    """)
    op.execute("DROP TYPE utility_type_old")

    # Restore NOT NULL on usage, unit, cost_per_unit
    # Note: any NULL rows will cause this to fail unless they are filled first
    op.alter_column('utilities', 'cost_per_unit',
                    existing_type=sa.Numeric(precision=10, scale=4),
                    nullable=False)
    op.alter_column('utilities', 'unit',
                    existing_type=sa.String(length=50),
                    nullable=False)
    op.alter_column('utilities', 'usage',
                    existing_type=sa.Numeric(precision=10, scale=2),
                    nullable=False)

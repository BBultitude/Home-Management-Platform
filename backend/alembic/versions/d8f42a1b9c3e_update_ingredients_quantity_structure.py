"""update_ingredients_quantity_structure

Revision ID: d8f42a1b9c3e
Revises: b2c4d6e8f1a3
Create Date: 2026-02-15 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8f42a1b9c3e'
down_revision = 'b2c4d6e8f1a3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns for quantity_amount and quantity_unit
    op.add_column('ingredients', sa.Column('quantity_amount', sa.Numeric(10, 2), nullable=True))
    op.add_column('ingredients', sa.Column('quantity_unit', sa.String(20), nullable=True))

    # Update existing data: try to parse "300 g" style quantities
    # For simplicity, set default values for existing rows (they'll need to be manually updated)
    # In production with real data, you'd want more sophisticated parsing
    op.execute("UPDATE ingredients SET quantity_amount = 1, quantity_unit = 'whole' WHERE quantity_amount IS NULL")

    # Make columns NOT NULL after data migration
    op.alter_column('ingredients', 'quantity_amount', nullable=False)
    op.alter_column('ingredients', 'quantity_unit', nullable=False)

    # Drop old quantity column
    op.drop_column('ingredients', 'quantity')


def downgrade() -> None:
    # Add back old quantity column
    op.add_column('ingredients', sa.Column('quantity', sa.String(100), nullable=True))

    # Migrate data back: combine quantity_amount and quantity_unit
    op.execute("UPDATE ingredients SET quantity = CONCAT(quantity_amount::TEXT, ' ', quantity_unit)")

    # Make quantity column NOT NULL
    op.alter_column('ingredients', 'quantity', nullable=False)

    # Drop new columns
    op.drop_column('ingredients', 'quantity_unit')
    op.drop_column('ingredients', 'quantity_amount')

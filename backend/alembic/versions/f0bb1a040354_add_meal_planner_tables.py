"""add_meal_planner_tables

Revision ID: f0bb1a040354
Revises: aef19fde6c5d
Create Date: 2026-02-13 16:12:17.418245

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'f0bb1a040354'
down_revision = 'aef19fde6c5d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create recipes table
    op.create_table(
        'recipes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('steps', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False),
    )

    # Create index on recipe name for search
    op.create_index('idx_recipes_name', 'recipes', ['name'])

    # Create ingredients table
    op.create_table(
        'ingredients',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('recipe_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('quantity', sa.String(100), nullable=False),
        sa.Column('sort_order', sa.Integer, nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE'),
    )

    # Create indexes for ingredients
    op.create_index('idx_ingredients_recipe', 'ingredients', ['recipe_id'])
    op.create_index('idx_ingredients_name', 'ingredients', ['name'])

    # Create week_plans table
    op.create_table(
        'week_plans',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('week_starting', sa.Date, nullable=False, unique=True),
        sa.Column('monday_meal_id', UUID(as_uuid=True), nullable=True),
        sa.Column('tuesday_meal_id', UUID(as_uuid=True), nullable=True),
        sa.Column('wednesday_meal_id', UUID(as_uuid=True), nullable=True),
        sa.Column('thursday_meal_id', UUID(as_uuid=True), nullable=True),
        sa.Column('friday_meal_id', UUID(as_uuid=True), nullable=True),
        sa.Column('saturday_meal_id', UUID(as_uuid=True), nullable=True),
        sa.Column('sunday_meal_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['monday_meal_id'], ['recipes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['tuesday_meal_id'], ['recipes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['wednesday_meal_id'], ['recipes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['thursday_meal_id'], ['recipes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['friday_meal_id'], ['recipes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['saturday_meal_id'], ['recipes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['sunday_meal_id'], ['recipes.id'], ondelete='SET NULL'),
    )

    # Create index on week_starting for queries
    op.create_index('idx_week_plans_starting', 'week_plans', ['week_starting'])


def downgrade() -> None:
    # Drop indexes and tables in reverse order
    op.drop_index('idx_week_plans_starting', table_name='week_plans')
    op.drop_table('week_plans')

    op.drop_index('idx_ingredients_name', table_name='ingredients')
    op.drop_index('idx_ingredients_recipe', table_name='ingredients')
    op.drop_table('ingredients')

    op.drop_index('idx_recipes_name', table_name='recipes')
    op.drop_table('recipes')

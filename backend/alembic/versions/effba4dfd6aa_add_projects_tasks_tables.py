"""add_projects_tasks_tables

Revision ID: effba4dfd6aa
Revises: ca7966545e30
Create Date: 2026-02-13 16:02:22.399567

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'effba4dfd6aa'
down_revision = 'ca7966545e30'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create projects table first (referenced by priority_items)
    op.create_table(
        'projects',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('project_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('priority_item_id', UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='Planned'),
        sa.Column('start_date', sa.Date, nullable=True),
        sa.Column('completion_date', sa.Date, nullable=True),
        sa.Column('budget', sa.Numeric(12, 2), nullable=True),
        sa.Column('actual_cost', sa.Numeric(12, 2), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False),
    )

    # Create indexes for projects
    op.create_index('idx_projects_status', 'projects', ['status'])

    # Create priority_items table
    op.create_table(
        'priority_items',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('description', sa.String(500), nullable=False),
        sa.Column('cost', sa.Numeric(12, 2), nullable=False),
        sa.Column('severity', sa.Integer, nullable=False),
        sa.Column('frequency', sa.Integer, nullable=False),
        sa.Column('benefit_score', sa.Integer, nullable=False),
        sa.Column('cost_score', sa.Integer, nullable=False),
        sa.Column('net_score', sa.Integer, nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='Pending'),
        sa.Column('project_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.CheckConstraint('severity >= 1 AND severity <= 5', name='check_severity_range'),
        sa.CheckConstraint('frequency >= 1 AND frequency <= 5', name='check_frequency_range'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='SET NULL'),
    )

    # Create indexes for priority_items
    op.create_index('idx_priority_items_status', 'priority_items', ['status'])
    op.create_index('idx_priority_items_net_score', 'priority_items', ['net_score'], postgresql_ops={'net_score': 'DESC'})
    op.create_index('idx_priority_items_project', 'priority_items', ['project_id'])

    # Add foreign key from projects to priority_items (circular reference)
    op.create_foreign_key('fk_projects_priority_item_id', 'projects', 'priority_items', ['priority_item_id'], ['id'], ondelete='SET NULL')
    op.create_index('idx_projects_priority_item', 'projects', ['priority_item_id'])

    # Create quotes table
    op.create_table(
        'quotes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('project_id', UUID(as_uuid=True), nullable=False),
        sa.Column('contractor_name', sa.String(255), nullable=False),
        sa.Column('contact_phone', sa.String(50), nullable=True),
        sa.Column('contact_email', sa.String(255), nullable=True),
        sa.Column('quote_amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('quote_date', sa.Date, nullable=False),
        sa.Column('expiry_date', sa.Date, nullable=True),
        sa.Column('scope_of_work', sa.Text, nullable=True),
        sa.Column('selected', sa.Boolean, server_default='false', nullable=False),
        sa.Column('document_id', UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['files.id'], ondelete='SET NULL'),
    )

    # Create indexes for quotes
    op.create_index('idx_quotes_project', 'quotes', ['project_id'])
    op.create_index('idx_quotes_expiry', 'quotes', ['expiry_date'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('idx_quotes_expiry', table_name='quotes')
    op.drop_index('idx_quotes_project', table_name='quotes')
    op.drop_table('quotes')

    op.drop_index('idx_projects_priority_item', table_name='projects')
    op.drop_constraint('fk_projects_priority_item_id', 'projects', type_='foreignkey')

    op.drop_index('idx_priority_items_project', table_name='priority_items')
    op.drop_index('idx_priority_items_net_score', table_name='priority_items')
    op.drop_index('idx_priority_items_status', table_name='priority_items')
    op.drop_table('priority_items')

    op.drop_index('idx_projects_status', table_name='projects')
    op.drop_table('projects')

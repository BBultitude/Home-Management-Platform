"""add_knowledge_base_tables

Revision ID: aef19fde6c5d
Revises: effba4dfd6aa
Create Date: 2026-02-13 16:07:59.528981

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, TSVECTOR


# revision identifiers, used by Alembic.
revision = 'aef19fde6c5d'
down_revision = 'effba4dfd6aa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create knowledge_articles table
    op.create_table(
        'knowledge_articles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('article_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('data', JSONB, nullable=False),
        sa.Column('tags', ARRAY(sa.String), nullable=True),
        sa.Column('search_vector', TSVECTOR, nullable=True),
        sa.Column('created_by', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False),
        sa.CheckConstraint(
            "article_type IN ('Measurement', 'Paint', 'TechDevice', 'StorageLocation', 'Vehicle', 'EmergencyContact', 'Appliance', 'Vendor')",
            name='check_article_type'
        ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    )

    # Create indexes for knowledge_articles
    op.create_index('idx_knowledge_type', 'knowledge_articles', ['article_type'])
    op.create_index('idx_knowledge_search', 'knowledge_articles', ['search_vector'], postgresql_using='gin')

    # Create knowledge_attachments table
    op.create_table(
        'knowledge_attachments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('article_id', UUID(as_uuid=True), nullable=False),
        sa.Column('file_id', sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['knowledge_articles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['file_id'], ['files.id'], ondelete='CASCADE'),
    )

    # Create indexes for knowledge_attachments
    op.create_index('idx_knowledge_attachments_article', 'knowledge_attachments', ['article_id'])
    op.create_index('idx_knowledge_attachments_file', 'knowledge_attachments', ['file_id'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_knowledge_attachments_file', table_name='knowledge_attachments')
    op.drop_index('idx_knowledge_attachments_article', table_name='knowledge_attachments')
    op.drop_table('knowledge_attachments')

    op.drop_index('idx_knowledge_search', table_name='knowledge_articles')
    op.drop_index('idx_knowledge_type', table_name='knowledge_articles')
    op.drop_table('knowledge_articles')

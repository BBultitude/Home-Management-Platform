"""add_assets_documents_tables

Revision ID: ca7966545e30
Revises: 8d07792f10cc
Create Date: 2026-02-13 15:56:18.997364

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY


# revision identifiers, used by Alembic.
revision = 'ca7966545e30'
down_revision = '8d07792f10cc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create insurance_policies table
    op.create_table(
        'insurance_policies',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('policy_type', sa.String(50), nullable=False),
        sa.Column('provider', sa.String(255), nullable=False),
        sa.Column('policy_number', sa.String(255), nullable=True),
        sa.Column('coverage_amount', sa.Numeric(12, 2), nullable=True),
        sa.Column('premium', sa.Numeric(10, 2), nullable=False),
        sa.Column('premium_frequency', sa.String(50), nullable=False),
        sa.Column('excess', sa.Numeric(10, 2), nullable=True),
        sa.Column('renewal_date', sa.Date, nullable=False),
        sa.Column('coverage_notes', sa.Text, nullable=True),
        sa.Column('document_id', sa.Integer, nullable=True),
        sa.Column('vehicle_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['files.id'], ondelete='SET NULL'),
    )

    # Create index on renewal_date for alert queries
    op.create_index('idx_insurance_renewal', 'insurance_policies', ['renewal_date'])

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('document_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('tags', ARRAY(sa.String), nullable=True),
        sa.Column('uploaded_date', sa.Date, server_default=sa.text('CURRENT_DATE'), nullable=False),
        sa.Column('expiry_date', sa.Date, nullable=True),
        sa.Column('file_id', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['file_id'], ['files.id'], ondelete='CASCADE'),
    )

    # Create indexes for query optimization
    op.create_index('idx_documents_type', 'documents', ['document_type'])
    op.create_index('idx_documents_expiry', 'documents', ['expiry_date'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_documents_expiry', table_name='documents')
    op.drop_index('idx_documents_type', table_name='documents')
    op.drop_index('idx_insurance_renewal', table_name='insurance_policies')

    # Drop tables
    op.drop_table('documents')
    op.drop_table('insurance_policies')

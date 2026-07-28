"""Add SOW funnel columns to Analytics

Revision ID: add_sow_funnel_columns_to_analytics
Revises: add_user_email_to_analytics
Create Date: 2026-01-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
# Keep revision id short enough for existing alembic_version VARCHAR(32)
revision = 'add_sow_funnel_cols'
down_revision = 'add_user_email_to_analytics'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('analytics', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sow_generate_clicked', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('sow_downloaded', sa.Boolean(), nullable=True))


def downgrade():
    with op.batch_alter_table('analytics', schema=None) as batch_op:
        batch_op.drop_column('sow_downloaded')
        batch_op.drop_column('sow_generate_clicked')



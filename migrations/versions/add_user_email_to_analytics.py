"""Add user_email to Analytics

Revision ID: add_user_email_to_analytics
Revises: f97cb127d875
Create Date: 2026-01-06

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_email_to_analytics'
down_revision = 'f97cb127d875'
branch_labels = None
depends_on = None


def upgrade():
    # Column was already manually added in production; use IF NOT EXISTS to keep migration idempotent.
    op.execute("ALTER TABLE analytics ADD COLUMN IF NOT EXISTS user_email VARCHAR(256);")


def downgrade():
    with op.batch_alter_table('analytics', schema=None) as batch_op:
        batch_op.drop_column('user_email')



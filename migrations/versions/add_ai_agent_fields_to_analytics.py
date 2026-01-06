"""add ai agent model and complexity to analytics

Revision ID: add_ai_agent_fields_to_analytics
Revises: 9106b3dc75c4
Create Date: 2025-12-12
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_ai_agent_fields_to_analytics'
down_revision = '9106b3dc75c4'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('analytics') as batch_op:
        batch_op.add_column(sa.Column('ai_agent_model', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('ai_agent_complexity', sa.String(length=32), nullable=True))


def downgrade():
    with op.batch_alter_table('analytics') as batch_op:
        batch_op.drop_column('ai_agent_complexity')
        batch_op.drop_column('ai_agent_model')




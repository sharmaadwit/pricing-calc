"""Add funnel_events table for step-level funnel tracking

Revision ID: add_funnel_events
Revises: add_sow_funnel_cols
Create Date: 2026-01-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_funnel_events'
down_revision = 'add_sow_funnel_cols'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'funnel_events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('user_email', sa.String(length=256), nullable=True),
        sa.Column('calculation_id', sa.String(length=64), nullable=True),
        sa.Column('step', sa.String(length=32), nullable=False),
        sa.Column('route', sa.String(length=16), nullable=True),
        sa.Column('country', sa.String(length=64), nullable=True),
        sa.Column('region', sa.String(length=64), nullable=True),
    )


def downgrade():
    op.drop_table('funnel_events')



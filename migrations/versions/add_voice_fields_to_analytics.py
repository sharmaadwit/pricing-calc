"""add voice fields to analytics

Revision ID: add_voice_fields_to_analytics
Revises: f97cb127d875_add_user_name_to_analytics
Create Date: 2025-10-31
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_voice_fields_to_analytics'
down_revision = 'f97cb127d875'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('analytics') as batch_op:
        batch_op.add_column(sa.Column('channel_type', sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column('voice_mandays', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('voice_dev_cost', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('voice_platform_fee', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('whatsapp_setup_fee', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('pstn_inbound_ai_minutes', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('pstn_inbound_committed', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('pstn_outbound_ai_minutes', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('pstn_outbound_committed', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('pstn_manual_minutes', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('pstn_manual_committed', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('whatsapp_voice_outbound_minutes', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('whatsapp_voice_inbound_minutes', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('voice_cost_pstn_inbound', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('voice_cost_pstn_outbound', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('voice_cost_pstn_manual', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('voice_cost_wa_outbound', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('voice_cost_wa_inbound', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('voice_total_cost', sa.Float(), nullable=True))


def downgrade():
    with op.batch_alter_table('analytics') as batch_op:
        batch_op.drop_column('voice_total_cost')
        batch_op.drop_column('voice_cost_wa_inbound')
        batch_op.drop_column('voice_cost_wa_outbound')
        batch_op.drop_column('voice_cost_pstn_manual')
        batch_op.drop_column('voice_cost_pstn_outbound')
        batch_op.drop_column('voice_cost_pstn_inbound')
        batch_op.drop_column('whatsapp_voice_inbound_minutes')
        batch_op.drop_column('whatsapp_voice_outbound_minutes')
        batch_op.drop_column('pstn_manual_committed')
        batch_op.drop_column('pstn_manual_minutes')
        batch_op.drop_column('pstn_outbound_committed')
        batch_op.drop_column('pstn_outbound_ai_minutes')
        batch_op.drop_column('pstn_inbound_committed')
        batch_op.drop_column('pstn_inbound_ai_minutes')
        batch_op.drop_column('whatsapp_setup_fee')
        batch_op.drop_column('voice_platform_fee')
        batch_op.drop_column('voice_dev_cost')
        batch_op.drop_column('voice_mandays')
        batch_op.drop_column('channel_type')



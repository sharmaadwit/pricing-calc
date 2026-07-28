"""merge heads after voice analytics

Revision ID: 9106b3dc75c4
Revises: add_voice_fields_to_analytics, add_voice_notes_columns, d1608aa11fcb
Create Date: 2025-10-31 16:54:14.335529

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9106b3dc75c4'
down_revision = ('add_voice_fields_to_analytics', 'add_voice_notes_columns', 'd1608aa11fcb')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass

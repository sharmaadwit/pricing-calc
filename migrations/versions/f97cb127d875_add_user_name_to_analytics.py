"""Add user_name to Analytics

Revision ID: f97cb127d875
Revises: 9f7897f373d9
Create Date: 2025-06-30 22:40:43.941007

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f97cb127d875'
down_revision = '9f7897f373d9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('analytics', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_name', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('currency', sa.String(length=8), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('analytics', schema=None) as batch_op:
        batch_op.drop_column('user_name')
        batch_op.drop_column('currency')

    # ### end Alembic commands ###

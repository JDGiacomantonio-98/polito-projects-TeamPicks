"""empty message

Revision ID: 933e39bfb63c
Revises: 41b27620cdab
Create Date: 2020-05-22 00:36:23.913408

"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '933e39bfb63c'
down_revision = '41b27620cdab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('owners', sa.Column('member_since', sa.DateTime(), nullable=False, default=datetime.utcnow()))
    op.add_column('users', sa.Column('member_since', sa.DateTime(), nullable=False, default=datetime.utcnow()))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'member_since')
    op.drop_column('owners', 'member_since')
    # ### end Alembic commands ###

"""empty message

Revision ID: f52e677c9e20
Revises: d2e377f9ca8e
Create Date: 2025-05-08 12:18:03.899029

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f52e677c9e20'
down_revision = 'd2e377f9ca8e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('goal', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title', sa.String(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('goal', schema=None) as batch_op:
        batch_op.drop_column('title')

    # ### end Alembic commands ###

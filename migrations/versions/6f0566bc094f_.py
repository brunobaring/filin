"""empty message

Revision ID: 6f0566bc094f
Revises: ca9582181f28
Create Date: 2021-02-10 23:57:09.436468

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f0566bc094f'
down_revision = 'ca9582181f28'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('user_role_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'user', 'user_role', ['user_role_id'], ['id_'])
    op.drop_column('user', 'admin')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('admin', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_column('user', 'user_role_id')
    # ### end Alembic commands ###

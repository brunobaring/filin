"""empty message

Revision ID: 1112fbad86ed
Revises: 4a9ca6c3245a
Create Date: 2021-02-10 23:12:38.859309

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1112fbad86ed'
down_revision = '4a9ca6c3245a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_role_scope',
    sa.Column('id_', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('scope_id', sa.Integer(), nullable=False),
    sa.Column('user_role_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['scope_id'], ['scope.id_'], ),
    sa.ForeignKeyConstraint(['user_role_id'], ['user_role.id_'], ),
    sa.PrimaryKeyConstraint('id_')
    )
    op.drop_constraint('user_role_scope_id_fkey', 'user_role', type_='foreignkey')
    op.drop_column('user_role', 'scope_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_role', sa.Column('scope_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('user_role_scope_id_fkey', 'user_role', 'scope', ['scope_id'], ['id_'])
    op.drop_table('user_role_scope')
    # ### end Alembic commands ###
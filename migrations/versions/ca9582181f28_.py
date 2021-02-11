"""empty message

Revision ID: ca9582181f28
Revises: 1112fbad86ed
Create Date: 2021-02-10 23:54:48.923367

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca9582181f28'
down_revision = '1112fbad86ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'company', ['name'])
    op.create_unique_constraint(None, 'contact_channel', ['type_'])
    op.create_unique_constraint(None, 'scope', ['name'])
    op.create_unique_constraint(None, 'user_role', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_role', type_='unique')
    op.drop_constraint(None, 'scope', type_='unique')
    op.drop_constraint(None, 'contact_channel', type_='unique')
    op.drop_constraint(None, 'company', type_='unique')
    # ### end Alembic commands ###

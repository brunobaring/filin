"""empty message

Revision ID: 8423f1d7cb04
Revises: 968677ffc174
Create Date: 2021-02-18 19:54:10.282352

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8423f1d7cb04'
down_revision = '968677ffc174'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('company', sa.Column('names', sa.String(length=255), nullable=True))
    op.add_column('company', sa.Column('namess', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('company', 'namess')
    op.drop_column('company', 'names')
    # ### end Alembic commands ###

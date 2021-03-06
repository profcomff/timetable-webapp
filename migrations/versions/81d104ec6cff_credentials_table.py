"""Credentials table

Revision ID: 81d104ec6cff
Revises: 
Create Date: 2022-03-16 17:38:11.157247

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '81d104ec6cff'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('credentials',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(), nullable=False),
    sa.Column('scope', postgresql.JSON(astext_type=sa.Text()), nullable=False),
    sa.Column('group', sa.String(), nullable=False),
    sa.Column('prompt', sa.String(), nullable=False),
    sa.Column('authuser', sa.Integer(), nullable=False),
    sa.Column('hd', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('credentials')
    # ### end Alembic commands ###

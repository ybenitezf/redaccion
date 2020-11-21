"""add models board and article

Revision ID: 3106edc24862
Revises: efb9cf4605ed
Create Date: 2020-11-17 15:30:49.684864

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3106edc24862'
down_revision = 'efb9cf4605ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('board',
    sa.Column('name', sa.String(length=60), nullable=False),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('article',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('board_id', sa.String(length=60), nullable=True),
    sa.ForeignKeyConstraint(['board_id'], ['board.name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('article')
    op.drop_table('board')
    # ### end Alembic commands ###

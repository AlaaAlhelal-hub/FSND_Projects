"""empty message

Revision ID: 873f03f5774a
Revises: 7d7cc8a1fd12
Create Date: 2020-10-13 18:34:03.240245

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '873f03f5774a'
down_revision = '7d7cc8a1fd12'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('artists', 'image_link',
               existing_type=sa.VARCHAR(length=500),
               nullable=False)
    op.alter_column('artists', 'seeking_talent',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('artists', 'website',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('artists', 'website',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('artists', 'seeking_talent',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('artists', 'image_link',
               existing_type=sa.VARCHAR(length=500),
               nullable=True)
    # ### end Alembic commands ###

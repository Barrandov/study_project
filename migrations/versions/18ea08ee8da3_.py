"""empty message

Revision ID: 18ea08ee8da3
Revises: 9399fd822fb8
Create Date: 2020-05-29 15:48:20.027474

"""
from alembic import op
import sqlalchemy as sa
from tools import convert

# revision identifiers, used by Alembic.
revision = '18ea08ee8da3'
down_revision = '9399fd822fb8'
branch_labels = None
depends_on = None


def upgrade():
    convert()


def downgrade():
    pass

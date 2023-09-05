"""Convert uuid column to VARCHAR(36)

Revision ID: 1f6fbd501def
Revises: e475ba15d3cd
Create Date: 2023-05-03 22:54:10.106756

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f6fbd501def'
down_revision = 'e475ba15d3cd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

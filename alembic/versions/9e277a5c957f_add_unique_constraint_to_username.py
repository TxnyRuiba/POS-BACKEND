"""Add unique constraint to Username

Revision ID: 9e277a5c957f
Revises: 
Create Date: 2025-12-09 21:33:54.211397

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e277a5c957f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_index("ix_Users_Username", "Users", ["Username"], unique=True)

def downgrade():
    op.drop_index("ix_Users_Username", table_name="Users")
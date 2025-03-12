"""create account table

Revision ID: ef1dcb0ae1e1
Revises: 7d1d3348e12a
Create Date: 2025-03-12 06:08:23.622602

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef1dcb0ae1e1'
down_revision: Union[str, None] = '7d1d3348e12a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

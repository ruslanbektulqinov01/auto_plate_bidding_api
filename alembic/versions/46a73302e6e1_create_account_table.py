"""create account table

Revision ID: 46a73302e6e1
Revises: 2bc713e3bad4
Create Date: 2025-03-12 05:49:29.896884

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "46a73302e6e1"
down_revision: Union[str, None] = "2bc713e3bad4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

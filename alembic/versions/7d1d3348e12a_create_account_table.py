"""create account table

Revision ID: 7d1d3348e12a
Revises: d05999399c50
Create Date: 2025-03-12 06:01:31.655500

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7d1d3348e12a"
down_revision: Union[str, None] = "d05999399c50"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

"""Rename media url -> media uuid

Revision ID: 010b19d0c2ca
Revises: b6fc6735b713
Create Date: 2026-02-16 19:30:17.012782

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "010b19d0c2ca"
down_revision: Union[str, Sequence[str], None] = "b6fc6735b713"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new columns as nullable
    op.add_column(
        "notes_orms",
        sa.Column("video_uuid", sa.ARRAY(sa.String()), nullable=True),
    )
    op.add_column(
        "notes_orms",
        sa.Column("image_uuid", sa.ARRAY(sa.String()), nullable=True),
    )
    op.add_column(
        "notes_orms",
        sa.Column("audio_uuid", sa.ARRAY(sa.String()), nullable=True),
    )
    
    # Set default empty arrays
    op.execute("UPDATE notes_orms SET video_uuid = COALESCE(video_uuid, '{}')")
    op.execute("UPDATE notes_orms SET image_uuid = COALESCE(image_uuid, '{}')")
    op.execute("UPDATE notes_orms SET audio_uuid = COALESCE(audio_uuid, '{}')")
    
    # Drop old columns
    op.drop_column("notes_orms", "audio_urls")
    op.drop_column("notes_orms", "image_urls")
    op.drop_column("notes_orms", "video_urls")


def downgrade() -> None:
    """Downgrade schema."""
    # Restore old columns
    op.add_column(
        "notes_orms",
        sa.Column(
            "video_urls",
            postgresql.ARRAY(sa.VARCHAR()),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "notes_orms",
        sa.Column(
            "image_urls",
            postgresql.ARRAY(sa.VARCHAR()),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "notes_orms",
        sa.Column(
            "audio_urls",
            postgresql.ARRAY(sa.VARCHAR()),
            autoincrement=False,
            nullable=False,
        ),
    )
    
    # Drop new columns
    op.drop_column("notes_orms", "audio_uuid")
    op.drop_column("notes_orms", "image_uuid")
    op.drop_column("notes_orms", "video_uuid")

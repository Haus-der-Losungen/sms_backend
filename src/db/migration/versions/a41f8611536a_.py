"""User Table Migration

Revision ID: a41f8611536a
Revises: 
Create Date: 2025-06-29 21:12:17.792942
"""

from typing import Sequence, Union, Tuple
from alembic import op
import sqlalchemy as sa
import datetime

# revision identifiers, used by Alembic.
revision: str = 'a41f8611536a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def timestamps(indexed: bool = False) -> Tuple[sa.Column, sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=indexed,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=indexed,
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean,
            nullable=False,
            server_default=sa.false(),
            index=indexed,
        ),
    )


def create_users_table() -> None:
    users_table = op.create_table(
        "users",
        sa.Column("user_id", sa.String(7), primary_key=True),
        sa.Column("role", sa.String(255), nullable=False),
        sa.Column("pin_hash", sa.String(255), nullable=False),
        *timestamps(indexed=True),
    )

    op.bulk_insert(
        users_table,
        [
            {
                "user_id": "1000001",
                "role": "admin",
                "pin_hash": "$5$rounds=535000$mJI/s6D18BiWkf7G$/SrYBhDrWTIDvzgcre3uzbpG0HI4lAd1GN2aWTjzJ56",  # PIN: 123456
            },
            {
                "user_id": "1000002",
                "role": "staff",
                "pin_hash": "$5$rounds=535000$mJI/s6D18BiWkf7G$/SrYBhDrWTIDvzgcre3uzbpG0HI4lAd1GN2aWTjzJ56",  # PIN: 123456
            },
            {
                "user_id": "1000003",
                "role": "student",
                "pin_hash": "$5$rounds=535000$mJI/s6D18BiWkf7G$/SrYBhDrWTIDvzgcre3uzbpG0HI4lAd1GN2aWTjzJ56",  # PIN: 123456
            },
            {
                "user_id": "1000004",
                "role": "other",
                "pin_hash": "$5$rounds=535000$mJI/s6D18BiWkf7G$/SrYBhDrWTIDvzgcre3uzbpG0HI4lAd1GN2aWTjzJ56",  # PIN: 123456
            },
        ],
    )


def create_profiles_table() -> None:
    profiles_table = op.create_table(
        "profiles",
        sa.Column("profile_id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(7), sa.ForeignKey("users.user_id"), nullable=False, unique=True),
        sa.Column("email", sa.String(100), nullable=False),
        sa.Column("first_name", sa.String(50), nullable=False),
        sa.Column("last_name", sa.String(50), nullable=False),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("gender", sa.String(10), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("photo", sa.String(255), nullable=True),  # Store photo path or URL
        sa.Column("marital_status", sa.String(20), nullable=True),
        sa.Column("emergency_contact", sa.String(20), nullable=True),
        *timestamps(indexed=True),
    )

    op.bulk_insert(
        profiles_table,
        [
            {
                "profile_id": "3f9d8e06-41c9-4d57-a548-b7696ef2ed7a",
                "user_id": "1000001",
                "email": "sem@example.com",
                "first_name": "Selorm",
                "last_name": "Sem",
                "phone": "1234567890",
                "gender": "female",
                "date_of_birth": datetime.date(1970, 1, 1),
                "photo": "https://example.com/photo.jpg",
                "marital_status": "single",
                "emergency_contact": "1234567890",
                "created_at": datetime.datetime(1970, 1, 1, 0, 0, 0),
                "updated_at": datetime.datetime(1970, 1, 1, 0, 0, 0),
                "is_deleted": 0,
            },
            {
                "profile_id": "1d4c2b91-89ae-4c21-9088-6e4c8208d263",
                "user_id": "1000002",
                "email": "annan@example.com",
                "first_name": "Jedel",
                "last_name": "Annan",
                "phone": "1234567891",
                "gender": "male",
                "date_of_birth": datetime.date(1970, 1, 1),
                "photo": "https://example.com/photo.jpg",
                "marital_status": "single",
                "emergency_contact": "1234567891",
                "created_at": datetime.datetime(1970, 1, 1, 0, 0, 0),
                "updated_at": datetime.datetime(1970, 1, 1, 0, 0, 0),
                "is_deleted": 0,
            },
            {
                "profile_id": "94d99c7b-1ae9-4b27-8ca2-3abdf1b4d740",
                "user_id": "1000003",
                "email": "kuzagbe@example.com",
                "first_name": "Johnson",
                "last_name": "Kuzagbe",
                "phone": "1234567892",
                "gender": "male",
                "date_of_birth": datetime.date(1970, 1, 1),
                "photo": "https://example.com/photo.jpg",
                "marital_status": "single",
                "emergency_contact": "1234567892",
                "created_at": datetime.datetime(1970, 1, 1, 0, 0, 0),
                "updated_at": datetime.datetime(1970, 1, 1, 0, 0, 0),
                "is_deleted": 0,
            },
            {
                "profile_id": "30e4de4f-729e-4f1e-9a79-b33954fd0834",
                "user_id": "1000004",
                "email": "rapha@example.com",
                "first_name": "Abena",
                "last_name": "Rapha",
                "phone": "1234567893",
                "gender": "female",
                "date_of_birth": datetime.date(1970, 1, 1),
                "photo": "https://example.com/photo.jpg",
                "marital_status": "single",
                "emergency_contact": "1234567893",
                "created_at": datetime.datetime(1970, 1, 1, 0, 0, 0),
                "updated_at": datetime.datetime(1970, 1, 1, 0, 0, 0),
                "is_deleted": 0,
            },
        ],
    )


def create_admins_table() -> None:
    admins_table = op.create_table(
        "admins",
        sa.Column('admin_id', sa.String(7), sa.ForeignKey('users.user_id'), primary_key=True, nullable=False, unique=True),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.text("0")),  # SQLite uses 0/1 for booleans
        sa.Column('permissions', sa.JSON(), nullable=False, server_default=sa.text("'{}'")),  # Use sa.JSON for cross-db
        *timestamps(indexed=True),
    )
    op.bulk_insert(
        admins_table,
        [
            {
                "admin_id": "1000001",
                "is_admin": 1,
                "permissions": '{}',
                
            },
            {
                "admin_id": "1000002",
                "is_admin": 0,
                "permissions": '{}',
               
            },
            {
                "admin_id": "1000003",
                "is_admin": 0,
                "permissions": '{}',
               
            },
            {
                "admin_id": "1000004",
                "is_admin": 0,
                "permissions": '{}',
               
            },
        ],
    )


def upgrade() -> None:
    create_users_table()
    create_profiles_table()
    create_admins_table()

def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS admins")
    op.execute("DROP TABLE IF EXISTS profiles")
    op.execute("DROP TABLE IF EXISTS users")

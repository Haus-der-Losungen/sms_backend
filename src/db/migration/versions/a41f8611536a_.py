"""User Table Migration

Revision ID: a41f8611536a
Revises: 
Create Date: 2025-06-29 21:12:17.792942

"""
from typing import Sequence, Union, Tuple
from datetime import datetime, timedelta

from alembic import op
import sqlalchemy as sa

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
        sa.Column("user_id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        *timestamps(),
    )

    op.bulk_insert(
        users_table,
        [
            {
                "user_id": "950eeb54-b46c-4a50-a08d-ea52e0e0e4f5",
                "email": "Sem@outlook.com",
                "password_hash": "$2b$12$EGCcBNy8.02Md9CRoPhbSOi/.v2Wp8NSjcEvNcFGTSGMekR4an4Xm",  # banana123
            },
            {
                "user_id": "21c4d981-16b5-421b-a489-1040747e2051",
                "email": "Kuzagbe@yahoo.com",
                "password_hash": "$2b$12$tLybZswE36S/pAQffZQk8eY2PSheI5J6rNOkg0MSPXgZ49nxOJrVS",  # orange123
            },
            {
                "user_id": "b53d5f73-8453-4a0d-ab7b-ed210a867bc5",
                "email": "Quaye@email.com",
                "password_hash": "$2b$12$MxuIbk2w3xH8rLS7nU0UmuK5rpqldZagTDvBQtc7NqJ5l2OlSgweq",  # mango123
            },
            {
                "user_id": "a005d318-fe5f-4a5a-957b-7bc354d3ffd4",
                "email": "Annan@email.com",
                "password_hash": "$2b$12$Enu8iy58MeK3x4aUQpS7Ae1I6A3hxO6ESvTEzY3ljFVDMIx9FZbhG",  # apple123
            },
        ],
    )


def create_profiles_table() -> None:
    profiles = op.create_table(
        "profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.user_id"), nullable=False, unique=True),
        sa.Column("email", sa.String(100), nullable=False, unique=True),
        sa.Column("first_name", sa.String(50), nullable=False),
        sa.Column("last_name", sa.String(50), nullable=False),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("gender", sa.String(10), nullable=False),
        sa.Column("user_type", sa.String(20), nullable=False),  # Corrected key name
        *timestamps(),
    )

    op.bulk_insert(
        profiles,
        [
            {
                "id": "950eeb54-b46c-4a50-a08d-ea52e0e0e4f8",
                "user_id": "950eeb54-b46c-4a50-a08d-ea52e0e0e4f5",
                "email": "Sem@outlook.com",
                "first_name": "Selorm",
                "last_name": "Sem",
                "phone": "0241234567",
                "gender": "Female",
                "user_type": "student",
            },
            {
                "id": "950eeb54-b46c-4a50-a08d-ea52e0e0e4f9",
                "user_id": "21c4d981-16b5-421b-a489-1040747e2051",
                "email": "Kuzagbe@yahoo.com",
                "first_name": "Jhnsn",
                "last_name": "Kuzagbe",
                "phone": "0241234567",
                "gender": "Male",
                "user_type": "admin",
            },
            {
                "id": "950eeb54-b46c-4a50-a08d-ea52e0e0e4f7",
                "user_id": "b53d5f73-8453-4a0d-ab7b-ed210a867bc5",
                "email": "Quaye@email.com",
                "first_name": "Morrison",
                "last_name": "Quaye",
                "phone": "0241234567",
                "gender": "Male",
                "user_type": "staff",
            },
            {
                "id": "5b2035bd-3059-457e-bc90-f9dc6210d509",
                "user_id": "a005d318-fe5f-4a5a-957b-7bc354d3ffd4",
                "email": "Annan@email.com",
                "first_name": "JD",
                "last_name": "Annan",
                "phone": "0241234567",
                "gender": "Male",
                "user_type": "super admin",
            },
        ],
    )


def upgrade() -> None:
    create_users_table()
    create_profiles_table()


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS profiles")
    op.execute("DROP TABLE IF EXISTS users")

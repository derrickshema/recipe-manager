"""add customer role to system_role enum

Revision ID: add_customer_role_001
Revises: 0f3ee4a5926f
Create Date: 2025-12-24 22:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_customer_role_001'
down_revision = '0f3ee4a5926f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add CUSTOMER to the system_role enum (if it doesn't already exist)
    # Using a DO block to check existence first - PostgreSQL doesn't have IF NOT EXISTS for ADD VALUE
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_enum 
                WHERE enumlabel = 'CUSTOMER' 
                AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'system_role')
            ) THEN
                ALTER TYPE system_role ADD VALUE 'CUSTOMER';
            END IF;
        END
        $$;
    """)


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values easily
    # This would require recreating the enum type
    pass

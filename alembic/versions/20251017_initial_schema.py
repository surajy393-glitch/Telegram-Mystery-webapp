"""
Initial schema for Mystery Match and related tables.

This migration creates the core tables required for the async Mystery
Match API including users, matches, messages, blocked users, feature
flags, payments and content reports. Adjust columns and types as
necessary for your application.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251017_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Users table
    op.create_table(
        'users',
        sa.Column('tg_user_id', sa.BigInteger, primary_key=True),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('age', sa.Integer, nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('bio', sa.Text, nullable=True),
        sa.Column('interests', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('profile_photo_url', sa.String(length=300), nullable=True),
        sa.Column('is_premium', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.Column('premium_until', sa.DateTime, nullable=True),
    )

    # Payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.BigInteger, nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.tg_user_id'], ondelete='CASCADE'),
    )

    # Matches table
    op.create_table(
        'mystery_matches',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user1_id', sa.BigInteger, nullable=False),
        sa.Column('user2_id', sa.BigInteger, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('message_count', sa.Integer, nullable=False, server_default=sa.text('0')),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.text('true')),
        sa.Column('secret_chat_active', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.Column('unmatch_reason', sa.String(length=255), nullable=True),
        sa.Column('unmatch_by_user', sa.BigInteger, nullable=True),
        sa.Column('user1_unlock_level', sa.Integer, nullable=False, server_default=sa.text('0')),
        sa.Column('user2_unlock_level', sa.Integer, nullable=False, server_default=sa.text('0')),
        sa.ForeignKeyConstraint(['user1_id'], ['users.tg_user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user2_id'], ['users.tg_user_id'], ondelete='CASCADE'),
    )

    # Messages table
    op.create_table(
        'match_messages',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('match_id', sa.Integer, nullable=False),
        sa.Column('sender_id', sa.BigInteger, nullable=False),
        sa.Column('message_text', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('is_secret_chat', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.ForeignKeyConstraint(['match_id'], ['mystery_matches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.tg_user_id'], ondelete='CASCADE'),
    )

    # Blocked users table
    op.create_table(
        'blocked_users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.BigInteger, nullable=False),
        sa.Column('blocked_user_id', sa.BigInteger, nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('user_id', 'blocked_user_id', name='uq_blocked_user_pair'),
        sa.ForeignKeyConstraint(['user_id'], ['users.tg_user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['blocked_user_id'], ['users.tg_user_id'], ondelete='CASCADE'),
    )

    # Feature flags table
    op.create_table(
        'feature_flags',
        sa.Column('flag_name', sa.String(length=100), primary_key=True),
        sa.Column('enabled', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
    )

    # Content reports table
    op.create_table(
        'content_reports',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('reporter_id', sa.BigInteger, nullable=False),
        sa.Column('reported_user_id', sa.BigInteger, nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=False),
        sa.Column('content_id', sa.String(length=100), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['reporter_id'], ['users.tg_user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reported_user_id'], ['users.tg_user_id'], ondelete='CASCADE'),
    )

def downgrade():
    op.drop_table('content_reports')
    op.drop_table('feature_flags')
    op.drop_table('blocked_users')
    op.drop_table('match_messages')
    op.drop_table('mystery_matches')
    op.drop_table('payments')
    op.drop_table('users')

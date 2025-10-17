"""
Initial schema for Mystery Match
Creates all necessary tables for the dating platform
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create initial schema"""
    
    # Users table
    op.create_table(
        'users',
        sa.Column('tg_user_id', sa.BigInteger(), primary_key=True),
        sa.Column('gender', sa.String(20)),
        sa.Column('age', sa.Integer()),
        sa.Column('city', sa.String(100)),
        sa.Column('bio', sa.Text()),
        sa.Column('interests', sa.Text()),
        sa.Column('profile_photo_url', sa.String(500)),
        sa.Column('is_premium', sa.Boolean(), default=False),
        sa.Column('premium_until', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('orientation', sa.String(50)),  # New: for inclusivity
    )
    
    # Mystery matches table
    op.create_table(
        'mystery_matches',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user1_id', sa.BigInteger(), sa.ForeignKey('users.tg_user_id')),
        sa.Column('user2_id', sa.BigInteger(), sa.ForeignKey('users.tg_user_id')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('message_count', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('user1_unlock_level', sa.Integer(), default=0),
        sa.Column('user2_unlock_level', sa.Integer(), default=0),
        sa.Column('secret_chat_active', sa.Boolean(), default=False),
        sa.Column('unmatch_reason', sa.String(200)),
        sa.Column('unmatch_by_user', sa.BigInteger()),
    )
    
    # Match messages table
    op.create_table(
        'match_messages',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('match_id', sa.Integer(), sa.ForeignKey('mystery_matches.id')),
        sa.Column('sender_id', sa.BigInteger(), sa.ForeignKey('users.tg_user_id')),
        sa.Column('message_text', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('is_secret_chat', sa.Boolean(), default=False),
    )
    
    # Blocked users table
    op.create_table(
        'blocked_users',
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.tg_user_id')),
        sa.Column('blocked_user_id', sa.BigInteger(), sa.ForeignKey('users.tg_user_id')),
        sa.Column('reason', sa.String(200)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('user_id', 'blocked_user_id'),
    )
    
    # Payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.tg_user_id')),
        sa.Column('amount', sa.Integer()),
        sa.Column('currency', sa.String(10)),
        sa.Column('status', sa.String(20)),
        sa.Column('payment_provider', sa.String(50)),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Feature flags table (NEW)
    op.create_table(
        'feature_flags',
        sa.Column('flag_name', sa.String(100), primary_key=True),
        sa.Column('enabled', sa.Boolean(), default=False),
        sa.Column('description', sa.Text()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_by', sa.String(100)),
    )
    
    # Reports table (NEW for moderation)
    op.create_table(
        'content_reports',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('reporter_id', sa.BigInteger(), sa.ForeignKey('users.tg_user_id')),
        sa.Column('reported_user_id', sa.BigInteger(), sa.ForeignKey('users.tg_user_id')),
        sa.Column('content_type', sa.String(50)),  # 'message', 'profile', 'photo'
        sa.Column('content_id', sa.String(100)),
        sa.Column('reason', sa.String(200)),
        sa.Column('status', sa.String(20), default='pending'),  # pending, reviewed, actioned
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('reviewed_at', sa.DateTime(timezone=True)),
        sa.Column('reviewed_by', sa.String(100)),
        sa.Column('action_taken', sa.String(200)),
    )
    
    # Create indexes
    op.create_index('idx_matches_users', 'mystery_matches', ['user1_id', 'user2_id'])
    op.create_index('idx_matches_active', 'mystery_matches', ['is_active'])
    op.create_index('idx_messages_match', 'match_messages', ['match_id'])
    op.create_index('idx_reports_status', 'content_reports', ['status'])


def downgrade():
    """Drop all tables"""
    op.drop_table('content_reports')
    op.drop_table('feature_flags')
    op.drop_table('payments')
    op.drop_table('blocked_users')
    op.drop_table('match_messages')
    op.drop_table('mystery_matches')
    op.drop_table('users')

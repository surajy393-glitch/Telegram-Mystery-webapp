"""
Add fantasy match tables
Creates tables for fantasy submissions and matches
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002_fantasy_tables'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    """Create fantasy match tables"""
    
    # Fantasy submissions table
    op.create_table(
        'fantasy_submissions',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.tg_user_id'), nullable=False),
        sa.Column('gender', sa.Text(), nullable=False),
        sa.Column('fantasy_text', sa.Text(), nullable=False),
        sa.Column('vibe', sa.Text(), nullable=False),
        sa.Column('keywords', postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('active', sa.Boolean(), default=True),
    )
    
    # Fantasy matches table
    op.create_table(
        'fantasy_matches',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('boy_id', sa.BigInteger(), sa.ForeignKey('users.tg_user_id'), nullable=False),
        sa.Column('girl_id', sa.BigInteger(), sa.ForeignKey('users.tg_user_id'), nullable=False),
        sa.Column('fantasy_key', sa.Text(), nullable=False),
        sa.Column('vibe', sa.Text(), nullable=False),
        sa.Column('common_keywords', postgresql.ARRAY(sa.Text())),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('notified_at', sa.DateTime(timezone=True)),
        sa.Column('status', sa.Text(), default='pending'),
    )
    
    # Confession roulette table
    op.create_table(
        'confession_roulette',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.tg_user_id'), nullable=False),
        sa.Column('confession_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('shown_count', sa.Integer(), default=0),
        sa.Column('active', sa.Boolean(), default=True),
    )
    
    # Create indexes
    op.create_index('idx_fantasy_submissions_user', 'fantasy_submissions', ['user_id'])
    op.create_index('idx_fantasy_submissions_active', 'fantasy_submissions', ['active'])
    op.create_index('idx_fantasy_matches_key', 'fantasy_matches', ['fantasy_key'])
    op.create_index('idx_confession_user', 'confession_roulette', ['user_id'])


def downgrade():
    """Drop fantasy match tables"""
    op.drop_table('confession_roulette')
    op.drop_table('fantasy_matches')
    op.drop_table('fantasy_submissions')

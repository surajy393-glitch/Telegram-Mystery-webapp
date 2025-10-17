#!/bin/bash

# GitHub Secret Protection Fix Script
# This script removes sensitive files from git history

echo "🔧 Fixing GitHub Secret Protection Issue..."

cd /app

# Step 1: Remove test_sendgrid.py from all history
echo "Step 1: Removing test_sendgrid.py from git history..."
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch test_sendgrid.py" \
  --prune-empty --tag-name-filter cat -- --all

# Step 2: Clean up refs
echo "Step 2: Cleaning up refs..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Step 3: Add to .gitignore (already done)
echo "Step 3: Verifying .gitignore..."
if ! grep -q "test_\*.py" .gitignore; then
    echo "test_*.py" >> .gitignore
fi

# Step 4: Force push (will be done manually)
echo ""
echo "✅ Git history cleaned!"
echo ""
echo "⚠️  IMPORTANT: You need to FORCE PUSH to GitHub:"
echo "   This will be done automatically by the Save to GitHub feature"
echo ""
echo "📝 What was done:"
echo "   - Removed test_sendgrid.py from all git history"
echo "   - Cleaned up git refs and garbage collected"
echo "   - Updated .gitignore to prevent future issues"
echo ""
echo "🔐 Security Reminder:"
echo "   - Your SendGrid API key was exposed in the commit"
echo "   - Consider regenerating it from SendGrid dashboard"
echo "   - Always use environment variables for secrets"

# Security Policy

## 🔒 Protecting Your API Keys

This project requires API tokens for Slack, Notion, and AWS services. **NEVER commit these to version control.**

### ✅ Safe Practices

1. **Always use `.env` file** for secrets (already in `.gitignore`)
2. **Copy from `.env.example`** and fill in your values
3. **Use placeholder values** in documentation
4. **Rotate tokens** if accidentally exposed

### 🚨 If You Accidentally Commit Secrets

1. **Immediately revoke** the exposed tokens in their respective services
2. **Generate new tokens** 
3. **Remove from git history**: `git filter-branch` or contact GitHub support
4. **Update your `.env`** with new tokens

### 📋 Required Environment Variables

```bash
# Never commit real values - use .env file
SLACK_BOT_TOKEN=xoxb-your-token-here
NOTION_TOKEN=secret_your-token-here
NOTION_DATABASE_ID=your-database-id-here
```

### 🔍 Reporting Security Issues

If you find a security vulnerability, please email: [your-email@example.com]

**Do not** create public GitHub issues for security vulnerabilities.
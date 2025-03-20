# Vercel Authentication Troubleshooting Guide

## Common Issues & Solutions

### 1. Login Not Working
If `vercel login` seems stuck:
1. Cancel the current process (Ctrl+C)
2. Try alternative login method:
```bash
vercel login --github
```

### 2. Manual Authentication
If automatic browser login fails:
1. Visit https://vercel.com/dashboard manually
2. Go to Settings → Tokens
3. Create a new token
4. Copy the token
5. Create/edit `~/.vercel/credentials.json`:
```json
{
  "token": "your_token_here"
}
```

### 3. CLI Issues
If Vercel CLI is not responding:
```bash
# 1. Uninstall Vercel
npm uninstall -g vercel

# 2. Clear npm cache
npm cache clean --force

# 3. Reinstall Vercel
npm install -g vercel@latest

# 4. Try logging in again
vercel login
```

### 4. Project Linking
If you get project errors:
```bash
# Remove existing link
rm -rf .vercel

# Login and relink
vercel link
```

### 5. Environment Variables
After login succeeds:
```bash
# 1. Set up environment variables
python setup_vercel_env.py

# 2. Verify they're set
vercel env ls

# 3. Deploy your app
python deploy.py
```

### 6. Network Issues
- Check if you can access vercel.com
- Try using a different network
- Disable VPN if you're using one
- Check firewall settings

### Getting Help
1. Run diagnostics:
```bash
vercel --debug
```

2. Check Vercel status:
- Visit https://www.vercel-status.com

3. Contact support:
- Open an issue at https://github.com/vercel/vercel/issues
- Join Vercel Discord: https://vercel.com/discord

Remember: You must be logged in before deploying. Run `vercel whoami` to verify your login status.
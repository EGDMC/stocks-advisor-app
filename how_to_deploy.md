# How to Deploy Your App and Get Your URL

1. First, install Node.js if you haven't already:
   - Download from: https://nodejs.org/
   - Choose the LTS (Long Term Support) version

2. Install Vercel CLI:
```bash
npm install -g vercel
```

3. Set up your Vercel account:
```bash
# This will guide you through account creation and authentication
python setup_vercel_account.py
```

If you already have a Vercel account:
```bash
vercel login
```

4. Set up environment variables:
```bash
# This will automatically configure Vercel with your Supabase credentials
python setup_vercel_env.py
```

5. Deploy your app:
```bash
vercel --prod
```

5. Your app URL will be shown after deployment in this format:
   - Production: https://your-app-name.vercel.app
   - Preview (for testing): https://your-app-name-git-main-username.vercel.app

6. You can also find your URL:
   - Go to https://vercel.com/dashboard
   - Click on your project
   - The URL will be shown at the top of the page

Need help? Run:
```bash
python test_setup.py  # to verify Supabase setup
vercel --help        # to see all deployment options
```

Monitor Your Deployment:
1. View deployment status:
```bash
vercel logs
```

2. Check deployment URL:
```bash
vercel list
```

3. View your project info:
```bash
vercel project ls
```

4. Monitor in Vercel Dashboard:
- Go to https://vercel.com/dashboard
- Select your project
- Click "Deployments" tab
- View logs and status

Troubleshooting:
- If deployment fails, check logs: `vercel logs`
- Verify env variables: `vercel env ls`
- Test locally: `vercel dev`
- Review build output in Vercel dashboard

Note: Your environment variables are automatically set up by setup_vercel_env.py
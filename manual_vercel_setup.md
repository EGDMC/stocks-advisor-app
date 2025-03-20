# Manual Vercel Project Setup Guide

1. **Go to Vercel Dashboard**
   - Visit https://vercel.com/dashboard
   - Sign in with your GitHub account if needed

2. **Create New Project**
   - Click "Add New..."
   - Select "Project"
   - Choose "Import Git Repository"
   - Select your stocks app repository

3. **Configure Project**
   - Project Name: `stocks-analysis-app`
   - Framework Preset: Choose "Other" since we have a custom setup
   - Root Directory: `./` (default)
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: `./` (default)

4. **Add Environment Variables**
   Add these environment variables in the project settings:

   ```
   SUPABASE_URL=https://glafyufufuuuieumgvqy.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdsYWZ5dWZ1ZnV1dWlldW1ndnF5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI0MzIzMzEsImV4cCI6MjA1ODAwODMzMX0.R5VKyduyQtA3loWj9nIPGlJ2TIzhq6jtW6_dQh9AIgU
   ```

   Steps:
   - Go to Project Settings
   - Click on "Environment Variables"
   - Add each variable one by one
   - Make sure to check "Production" environment

5. **Deploy**
   - After configuration, click "Deploy"
   - Wait for the build and deployment to complete

Your project should now be set up on Vercel with the correct environment variables!
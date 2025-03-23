# Netlify Deployment Guide for EGX 30 Stock Advisor

## Prerequisites
1. The deployment package (`netlify-deploy.zip`) is located at:
   ```
   C:\Users\VIP\Documents\Programming\Stocks App\netlify-deploy.zip
   ```

## Step-by-Step Deployment Guide

### 1. Access Netlify Dashboard
1. Go to [https://app.netlify.com/](https://app.netlify.com/)
2. Log in to your account
3. Click on "Sites" in the top navigation

### 2. Create New Site
1. Click the "Add new site" button
2. Select "Deploy manually"
3. In the file upload dialog:
   - Navigate to `C:\Users\VIP\Documents\Programming\Stocks App`
   - Select `netlify-deploy.zip`
   - Click "Open" to upload

### 3. Configure Environment Variables
1. Once the site is created, go to "Site settings" (Site configuration)
2. Find "Environment variables" in the left menu
3. Click "Add a variable"
4. Add the following variables:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   BACKEND_URL=your_backend_url
   API_KEY=your_api_key
   ```

### 4. Configure Build Settings
1. Go to "Build & deploy" in the left menu
2. Under "Build settings":
   - Build command: `cd netlify/functions && chmod +x build.sh && ./build.sh`
   - Publish directory: `public`
   - Functions directory: `netlify/functions`

### 5. Configure Functions
1. Still in "Build & deploy"
2. Find "Functions" section
3. Enable "Python Runtime"
4. Set Python version to 3.9

### 6. Deploy
1. Go to "Deploys" in the top navigation
2. Click "Trigger deploy" → "Deploy site"
3. Wait for deployment to complete

### 7. Verify Deployment
1. Once deployment is complete, click the generated site URL
2. Check that the homepage loads correctly
3. Test the API endpoint at: `/.netlify/functions/analyze`

### 8. Common Issues and Solutions

#### Size Limit Issues
If you see size limit warnings:
1. Go to "Functions" settings
2. Increase function size limit if needed
3. Consider splitting large functions

#### Build Errors
If the build fails:
1. Check build logs in "Deploys"
2. Verify Python version is set correctly
3. Ensure all environment variables are set

#### Runtime Errors
If functions fail:
1. Check function logs in "Functions" tab
2. Verify environment variables
3. Test locally using Netlify CLI

### 9. Post-Deployment Tasks

#### Set up Custom Domain (Optional)
1. Go to "Domain settings"
2. Click "Add custom domain"
3. Follow the DNS configuration steps

#### Enable HTTPS
1. Wait for Netlify's automatic SSL certificate
2. Should be ready in ~1 hour

#### Monitor Performance
1. Check "Analytics" tab
2. Monitor function execution times
3. Set up notifications for errors

## Troubleshooting

If you encounter issues:

1. **Build Failures**
   - Check the build logs
   - Verify requirements.txt is correct
   - Ensure build.sh has correct permissions

2. **Function Errors**
   - Check function logs
   - Verify environment variables
   - Test API endpoints

3. **Performance Issues**
   - Monitor function duration
   - Check memory usage
   - Consider function optimization

## Next Steps

After successful deployment:

1. Save your site URL
2. Update any services that need to connect to this deployment
3. Set up monitoring and alerts
4. Consider setting up CI/CD for future deployments

## Need Help?

- Netlify Docs: [https://docs.netlify.com/](https://docs.netlify.com/)
- Community Forums: [https://answers.netlify.com/](https://answers.netlify.com/)
- Support: [https://www.netlify.com/support/](https://www.netlify.com/support/)
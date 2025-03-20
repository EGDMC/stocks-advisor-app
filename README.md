# EGX 30 Stock Analysis Dashboard

A web application for analyzing EGX 30 stock market data with AI predictions and technical analysis.

## Deployment Guide

### 1. Supabase Setup
1. Create a free account at [Supabase](https://supabase.com)
2. Create a new project
3. Set up the database tables:
   - Go to SQL Editor in your Supabase dashboard
   - Open `src/database/tables.sql`
   - Copy and paste the SQL code into the editor
   - Click "Run" to create all required tables:
     * `market_data`: Stores price history with date, OHLCV data
     * `analysis_results`: Stores analysis results with trends and recommendations
     * `model_predictions`: Stores AI predictions with confidence levels
4. Copy your credentials:
   - Go to Project Settings > API
   - Copy the Project URL
   - Copy the `anon` public key

### 2. Environment Setup
1. Create a `.env` file from the template:
```bash
cp .env.example .env
```
2. Add your Supabase credentials to `.env`:
```
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_anon_key
```

### 3. Test Your Setup
1. Run the enhanced setup verification script:
```bash
python test_setup.py
```

The script provides an interactive and user-friendly setup experience:

📦 Package Installation
- Automatically installs required dependencies
- Verifies Python environment
- Handles version compatibility
- Manages all necessary packages

🔑 Configuration Setup
- Guides you through creating the `.env` file
- Helps input your Supabase credentials
- Validates configuration format
- Tests connectivity in real-time

🛠️ Database Setup
- Creates required tables automatically
- Verifies table permissions
- Tests data operations
- Ensures proper indexing

🔍 Verification Steps
1. Network connectivity check
2. Supabase credential validation
3. Database table creation/verification
4. Data operation testing
5. Permission validation

❌ Error Handling
- Clear error messages with solutions
- Step-by-step troubleshooting guides
- Links to relevant documentation
- Auto-recovery suggestions

If you encounter issues:
1. Follow the on-screen troubleshooting steps
2. Check Supabase project settings
3. Verify your credentials in `.env`
4. Ensure tables are created (use `src/database/tables.sql`)
5. Review logs for detailed error messages

The app will not deploy successfully until all tests pass.

### 4. Vercel Deployment
1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy the app:
```bash
vercel
```

4. Add environment variables in Vercel:
   - Go to your project settings
   - Add SUPABASE_URL and SUPABASE_KEY
   - Redeploy the application

### 4. Access Your App
- Once deployed, Vercel will provide you with a URL
- Your app will be accessible 24/7 at that URL
- Data will be stored persistently in Supabase

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
python src/app.py
```

## Features
- Real-time market analysis
- AI-powered predictions
- Technical analysis with support/resistance levels
- Interactive charts
- Persistent data storage
- Custom data upload support

## Stack
- Frontend: Dash/Plotly
- Backend: Python/Flask
- Database: Supabase
- Hosting: Vercel
- AI: Scikit-learn

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
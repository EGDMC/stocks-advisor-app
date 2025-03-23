# EGX 30 Stock Advisor

A machine learning-powered stock advisor for the Egyptian Exchange (EGX 30) index, providing market analysis and trading recommendations.

## Features

- 📈 Technical Analysis
- 🤖 Machine Learning Predictions
- 📊 Interactive Charts
- 📱 Responsive Web Interface
- 🔄 Real-time Updates
- 📝 Detailed Reports

## Project Structure

```
├── src/                  # Source code
│   ├── models/          # ML models
│   ├── database/        # Database handlers
│   ├── utils/           # Utilities
│   └── app.py          # Main application
├── data/                # Data directory
├── models/              # Trained models
├── public/              # Static files
└── netlify/             # Netlify configuration
    └── functions/       # Serverless functions
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/egx30-stock-advisor.git
cd egx30-stock-advisor
```

2. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# OR
.\.venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

## Local Development

1. Start the development server:
```bash
python src/app.py
```

2. Visit `http://localhost:8080` in your browser

## Deployment

### Netlify

1. Connect your GitHub repository to Netlify
2. Set up environment variables in Netlify dashboard
3. Deploy!

## Architecture

- Frontend: Dash + Bootstrap
- Backend: Python Flask
- ML Models: Scikit-learn
- Database: Supabase
- Hosting: Netlify

## API Reference

### Analysis Endpoint

```http
POST /api/analyze
```

Request Body:
```json
{
    "type": "bullish|bearish|custom",
    "data": {
        "dates": [...],
        "prices": [...],
        "volumes": [...]
    }
}
```

Response:
```json
{
    "trend": "Bullish|Bearish",
    "prediction": "Up|Down",
    "confidence": 95.5,
    "recommendation": "BUY|SELL|WAIT"
}
```

## Environment Variables

- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase API key
- `API_KEY`: Application API key
- `DEBUG`: Debug mode (True/False)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
import pandas as pd
import argparse
import json
from trading_advisor import TradingAdvisor
from datetime import datetime
import os

def run_analysis(data_file='data/egx30_sample.csv', model_type='mlp', should_train=False):
    """Run the stock analysis with given parameters"""
    print(f"\n=== Running EGX 30 Stock Analysis ===")
    print(f"Using data: {data_file}")
    print(f"Model type: {model_type.upper()}\n")
    
    # Load data
    print(f"Loading data...")
    df = pd.read_csv(data_file)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    print(f"Loaded {len(df)} data points")
    
    # Initialize advisor
    advisor = TradingAdvisor(ai_model_type=model_type)
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    model_path = f'models/default_{model_type}_model'
    
    if should_train or not os.path.exists(f'{model_path}_{model_type}.joblib'):
        print(f"\nTraining {model_type.upper()} model...")
        print("This may take a few moments...")
        advisor.train_ai_model(df)
        advisor.save_models(model_path)
        print("Model trained and saved successfully")
    else:
        print("\nLoading saved model...")
        advisor.load_models(model_path)
        print("Model loaded successfully")
    
    # Generate analysis
    print("\nAnalyzing market conditions...")
    analysis = advisor.analyze_trade_setup(df)
    
    # Display results
    print("\n=== Analysis Results ===\n")
    print(f"Market Trend: {analysis['market_structure']['trend']}")
    print(f"AI Prediction: {analysis['ai_prediction']['movement']} ({analysis['ai_prediction']['change_percent']:+.2f}%)")
    print(f"Confidence: {analysis['ai_prediction']['confidence']:.1f}%")
    print(f"Recommended Action: {analysis['trade_recommendation']['action']}")
    
    if analysis['trade_recommendation']['action'] != 'WAIT':
        print(f"Entry Price: {analysis['trade_recommendation']['entry']:.2f}")
        print(f"Target Price: {analysis['trade_recommendation']['target']:.2f}")
        print(f"Stop Loss: {analysis['trade_recommendation']['stop_loss']:.2f}")
        print(f"Risk-Reward Ratio: {analysis['trade_recommendation']['risk_reward_ratio']:.2f}")
    
    print(f"\nSummary:")
    print(analysis['summary'])
    
    return analysis

def main():
    parser = argparse.ArgumentParser(description='EGX 30 Stock Trading Advisor')
    parser.add_argument('--data', help='Path to CSV file containing stock data')
    parser.add_argument('--model', choices=['mlp', 'rf'], default='mlp',
                       help='AI model type to use (default: mlp)')
    parser.add_argument('--train', action='store_true', help='Force model retraining')
    parser.add_argument('--save-model', help='Save trained model to specified path')
    parser.add_argument('--load-model', help='Load trained model from specified path')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    
    if os.path.exists('data/egx30_sample.csv'):
        while True:
            print("\nEGX 30 Stock Analysis Options:")
            print("1. Analyze Bullish Market")
            print("2. Analyze Bearish Market")
            print("3. Custom Analysis")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                run_analysis('data/egx30_sample.csv', 'mlp')
            elif choice == '2':
                run_analysis('data/test_bearish.csv', 'mlp')
            elif choice == '3':
                args = parser.parse_args()
                if args.data:
                    analysis = run_analysis(args.data, args.model, args.train)
                    if args.json:
                        print(json.dumps(analysis, indent=2))
                else:
                    print("\nError: Please provide data file path for custom analysis")
                    print("Example: python src/main.py --data your_data.csv")
            elif choice == '4':
                print("\nExiting EGX 30 Stock Advisor. Goodbye!")
                break
            else:
                print("\nInvalid choice. Please enter 1, 2, 3, or 4.")
    else:
        print("Error: Sample data files not found. Please make sure 'data' directory exists with sample files.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAnalysis cancelled by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
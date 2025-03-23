from supabase import create_client
import pandas as pd
from datetime import datetime

class SupabaseHandler:
    def __init__(self, url, key):
        self.supabase = create_client(url, key)
    
    def save_market_data(self, data):
        """Save market data to Supabase"""
        # Convert DataFrame to records
        records = data.to_dict('records')
        for record in records:
            # Convert date to string if it's not already
            if isinstance(record['date'], pd.Timestamp):
                record['date'] = record['date'].strftime('%Y-%m-%d')
        
        # Insert data
        result = self.supabase.table('market_data').upsert(records).execute()
        return result
    
    def get_market_data(self, start_date=None, end_date=None):
        """Retrieve market data from Supabase"""
        query = self.supabase.table('market_data')
        
        if start_date:
            query = query.gte('date', start_date)
        if end_date:
            query = query.lte('date', end_date)
            
        result = query.order('date').execute()
        
        # Convert to DataFrame
        df = pd.DataFrame(result.data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
        return df
    
    def save_analysis_result(self, analysis_data):
        """Save analysis results to Supabase"""
        # Add timestamp
        analysis_data['created_at'] = datetime.now().isoformat()
        
        result = self.supabase.table('analysis_results').insert(analysis_data).execute()
        return result
    
    def get_latest_analysis(self):
        """Get the most recent analysis result"""
        result = self.supabase.table('analysis_results')\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        return result.data[0] if result.data else None
    
    def save_model_prediction(self, prediction_data):
        """Save model predictions to Supabase"""
        # Add timestamp
        prediction_data['created_at'] = datetime.now().isoformat()
        
        result = self.supabase.table('model_predictions').insert(prediction_data).execute()
        return result
    
    def get_recent_predictions(self, limit=10):
        """Get recent model predictions"""
        result = self.supabase.table('model_predictions')\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
            
        return result.data
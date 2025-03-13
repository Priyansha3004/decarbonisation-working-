import os
from supabase import create_client, Client
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

class SupabaseManager:
    def __init__(self):
        load_dotenv()
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
    def upload_emissions_data(self, data: pd.DataFrame):
        """Upload emissions data to Supabase"""
        # Convert DataFrame to dictionary format
        records = data.to_dict('records')
        
        # Add timestamp for tracking
        for record in records:
            record['uploaded_at'] = datetime.now().isoformat()
            
        try:
            result = self.supabase.table('cloud_emissions').insert(records).execute()
            print(f"Successfully uploaded {len(records)} records to cloud_emissions table")
            return result
        except Exception as e:
            print(f"Error uploading to Supabase: {e}")
            return None
            
    def upload_provider_metrics(self, data: pd.DataFrame):
        """Upload provider-specific metrics"""
        provider_metrics = data.groupby('Cloud Service Provider').agg({
            'Total Emissions (kg CO₂e)': 'sum',
            'Energy Consumption (MWh)': 'sum',
            'Renewable Energy Usage (%)': 'mean',
            'AI Workload (%)': 'mean',
            'PUE (Power Usage Effectiveness)': 'mean'
        }).round(2)
        
        records = provider_metrics.reset_index().to_dict('records')
        for record in records:
            record['calculated_at'] = datetime.now().isoformat()
            
        try:
            result = self.supabase.table('provider_metrics').insert(records).execute()
            print(f"Successfully uploaded provider metrics for {len(records)} providers")
            return result
        except Exception as e:
            print(f"Error uploading provider metrics: {e}")
            return None
            
    def upload_location_metrics(self, data: pd.DataFrame):
        """Upload location-based metrics"""
        location_metrics = data.groupby('Location').agg({
            'Total Emissions (kg CO₂e)': 'mean',
            'Energy Consumption (MWh)': 'mean',
            'Renewable Energy Usage (%)': 'mean'
        }).round(2)
        
        records = location_metrics.reset_index().to_dict('records')
        for record in records:
            record['calculated_at'] = datetime.now().isoformat()
            
        try:
            result = self.supabase.table('location_metrics').insert(records).execute()
            print(f"Successfully uploaded location metrics for {len(records)} locations")
            return result
        except Exception as e:
            print(f"Error uploading location metrics: {e}")
            return None

def main():
    # Load the data
    data = pd.read_csv('data/raw/Enhanced_Data_Center_Emissions_Database.csv')
    
    # Initialize Supabase manager
    db_manager = SupabaseManager()
    
    # Upload all datasets
    db_manager.upload_emissions_data(data)
    db_manager.upload_provider_metrics(data)
    db_manager.upload_location_metrics(data)

if __name__ == "__main__":
    main() 
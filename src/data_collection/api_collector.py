import os
import requests
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
from pathlib import Path
import numpy as np

load_dotenv()

class CarbonDataCollector:
    def __init__(self):
        self.gcp_api_key = os.getenv('GCP_API_KEY')
        self.aws_api_key = os.getenv('AWS_API_KEY')
        self.azure_api_key = os.getenv('AZURE_API_KEY')
        self.base_urls = {
            'gcp': 'https://cloudasset.googleapis.com/v1',
            'aws': 'https://sustainability.aws.amazon.com/v1',
            'azure': 'https://management.azure.com/sustainability/v1'
        }
        
        # Define data sources
        self.data_sources = {
            'electricity_factors': 'https://api.climatiq.io/data/v1/electricity_factors', # Example URL
            'github_data': 'https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv',
            'energy_data': 'https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv'
        }
        
        # Create data directories if they don't exist
        self.data_dir = Path('data')
        self.raw_dir = self.data_dir / 'raw'
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def _make_api_request(self, url, headers, params=None):
        """
        Make API request with error handling
        """
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None

    def collect_gcp_data(self):
        """
        Collect carbon emission data from Google Cloud Platform
        """
        headers = {
            'Authorization': f'Bearer {self.gcp_api_key}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_urls['gcp']}/sustainability/metrics"
        data = self._make_api_request(url, headers)
        
        if data:
            return pd.DataFrame({
                'timestamp': [datetime.now()],
                'provider': ['GCP'],
                'energy_consumption': [data.get('energy_kwh', 0)],
                'carbon_emissions': [data.get('carbon_kg', 0)],
                'data_transfer': [data.get('network_gb', 0)]
            })
        return pd.DataFrame()

    def collect_aws_data(self):
        """
        Collect carbon emission data from AWS
        """
        headers = {
            'x-api-key': self.aws_api_key,
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_urls['aws']}/carbon-metrics"
        data = self._make_api_request(url, headers)
        
        if data:
            return pd.DataFrame({
                'timestamp': [datetime.now()],
                'provider': ['AWS'],
                'energy_consumption': [data.get('energy_consumption', 0)],
                'carbon_emissions': [data.get('co2_emissions', 0)],
                'data_transfer': [data.get('data_transfer', 0)]
            })
        return pd.DataFrame()

    def collect_azure_data(self):
        """
        Collect carbon emission data from Azure
        """
        headers = {
            'Authorization': f'Bearer {self.azure_api_key}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_urls['azure']}/emissions"
        data = self._make_api_request(url, headers)
        
        if data:
            return pd.DataFrame({
                'timestamp': [datetime.now()],
                'provider': ['Azure'],
                'energy_consumption': [data.get('energy_usage', 0)],
                'carbon_emissions': [data.get('carbon_footprint', 0)],
                'data_transfer': [data.get('network_usage', 0)]
            })
        return pd.DataFrame()

    def collect_cloud_data(self):
        """
        Collect carbon emission data from all cloud providers
        Returns: DataFrame with standardized carbon metrics
        """
        dfs = []
        
        # Collect data from each provider
        gcp_data = self.collect_gcp_data()
        aws_data = self.collect_aws_data()
        azure_data = self.collect_azure_data()
        
        # Combine all data
        dfs.extend([gcp_data, aws_data, azure_data])
        
        # Concatenate all dataframes
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Save raw data
        if not combined_df.empty:
            self.save_raw_data(combined_df, 'all_providers')
            
        return combined_df

    def collect_training_benchmarks(self):
        """
        Collect AI training energy data from Stanford DAWNBench
        Returns: DataFrame with training energy metrics
        """
        # DAWNBench data URL (example)
        benchmark_url = "https://dawn.cs.stanford.edu/benchmark/data/latest.json"
        
        try:
            response = requests.get(benchmark_url)
            data = response.json()
            
            df = pd.DataFrame({
                'timestamp': [datetime.now()],
                'model_name': [entry.get('model_name') for entry in data],
                'training_time': [entry.get('training_time') for entry in data],
                'energy_consumption': [entry.get('energy_consumption') for entry in data],
                'carbon_footprint': [entry.get('carbon_footprint') for entry in data]
            })
            
            self.save_raw_data(df, 'training_benchmarks')
            return df
            
        except Exception as e:
            print(f"Error collecting benchmark data: {e}")
            return pd.DataFrame()

    def collect_github_carbon_data(self):
        """
        Collect CO2 emissions data from Our World in Data GitHub repository
        """
        try:
            df = pd.read_csv(self.data_sources['github_data'])
            # Select relevant columns
            columns = ['year', 'country', 'co2', 'co2_per_capita', 'energy_per_capita']
            df_filtered = df[columns].dropna()
            
            self.save_raw_data(df_filtered, 'github_carbon')
            return df_filtered
        except Exception as e:
            print(f"Error collecting GitHub carbon data: {e}")
            return pd.DataFrame()

    def collect_energy_data(self):
        """
        Collect energy consumption data from Our World in Data
        """
        try:
            df = pd.read_csv(self.data_sources['energy_data'])
            # Select relevant columns
            columns = ['year', 'country', 'electricity_generation', 
                      'electricity_consumption', 'energy_per_gdp']
            df_filtered = df[columns].dropna()
            
            self.save_raw_data(df_filtered, 'energy')
            return df_filtered
        except Exception as e:
            print(f"Error collecting energy data: {e}")
            return pd.DataFrame()

    def generate_sample_cloud_data(self):
        """
        Generate sample cloud usage data based on typical patterns
        """
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        
        data = {
            'timestamp': dates,
            'service_type': ['compute', 'storage', 'network'] * (len(dates) // 3 + 1),
            'energy_consumption': np.random.normal(100, 20, len(dates)),  # kWh
            'data_transfer': np.random.normal(500, 100, len(dates)),      # GB
            'carbon_emissions': np.random.normal(50, 10, len(dates))      # kg CO2
        }
        
        df = pd.DataFrame(data)
        self.save_raw_data(df, 'cloud_sample')
        return df

    def collect_local_csv_data(self, file_path):
        """
        Collect data from local CSV files
        """
        try:
            df = pd.read_csv(file_path)
            filename = Path(file_path).stem
            self.save_raw_data(df, f'local_{filename}')
            return df
        except Exception as e:
            print(f"Error reading local CSV file: {e}")
            return pd.DataFrame()

    def save_raw_data(self, df, source_name):
        """Save collected data to raw data directory"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"raw_data_{source_name}_{timestamp}.csv"
        df.to_csv(self.raw_dir / filename, index=False) 
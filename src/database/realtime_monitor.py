import os
from supabase import create_client, Client
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import time
import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import seaborn as sns
from IPython.display import clear_output

class RealtimeEmissionMonitor:
    def __init__(self):
        load_dotenv()
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Initialize real-time data storage
        self.current_emissions = pd.DataFrame()
        self.fig, self.axes = plt.subplots(2, 2, figsize=(15, 10))
        plt.style.use('seaborn')
        
    def start_realtime_monitoring(self):
        """Start real-time monitoring of emissions data"""
        def handle_broadcast(payload):
            """Handle real-time data updates"""
            try:
                new_data = payload['new']
                print(f"New data received at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Provider: {new_data['cloud_service_provider']}")
                print(f"Emissions: {new_data['total_emissions']} kg CO₂e")
                print("-" * 50)
                
                # Update visualizations
                self.update_visualizations(new_data)
                
            except Exception as e:
                print(f"Error handling broadcast: {e}")

        try:
            # Subscribe to real-time changes
            subscription = self.supabase.table('cloud_emissions').on('INSERT', handle_broadcast).subscribe()
            print("Real-time monitoring started. Waiting for updates...")
            
            # Keep the script running
            while True:
                time.sleep(1)
                
        except Exception as e:
            print(f"Error in real-time monitoring: {e}")
            
    def update_visualizations(self, new_data):
        """Update real-time visualizations"""
        # Clear previous plots
        for ax in self.axes.flat:
            ax.clear()
            
        # Get all current data
        emissions_data = self.supabase.table('cloud_emissions').select('*').execute()
        df = pd.DataFrame(emissions_data.data)
        
        # 1. Real-time emissions by provider
        provider_emissions = df.groupby('cloud_service_provider')['total_emissions'].sum()
        provider_emissions.plot(kind='bar', ax=self.axes[0,0])
        self.axes[0,0].set_title('Real-time Total Emissions by Provider')
        self.axes[0,0].set_ylabel('Total Emissions (kg CO₂e)')
        
        # 2. Emissions trend over time
        df['uploaded_at'] = pd.to_datetime(df['uploaded_at'])
        time_series = df.set_index('uploaded_at')['total_emissions'].resample('1H').mean()
        time_series.plot(ax=self.axes[0,1])
        self.axes[0,1].set_title('Emissions Trend')
        
        # 3. AI Workload Impact
        sns.scatterplot(data=df, 
                       x='ai_workload', 
                       y='total_emissions',
                       hue='cloud_service_provider',
                       ax=self.axes[1,0])
        self.axes[1,0].set_title('AI Workload vs Emissions')
        
        # 4. Renewable Energy Impact
        sns.scatterplot(data=df,
                       x='renewable_energy_usage',
                       y='total_emissions',
                       hue='cloud_service_provider',
                       ax=self.axes[1,1])
        self.axes[1,1].set_title('Renewable Energy vs Emissions')
        
        plt.tight_layout()
        plt.draw()
        plt.pause(0.1)

def simulate_real_time_data():
    """Simulate real-time data updates for testing"""
    db_manager = RealtimeEmissionMonitor()
    base_data = pd.read_csv('data/raw/Enhanced_Data_Center_Emissions_Database.csv')
    
    while True:
        # Randomly select and modify a record
        random_record = base_data.sample(n=1).to_dict('records')[0]
        random_record['uploaded_at'] = datetime.now().isoformat()
        
        # Add some random variation
        random_record['total_emissions'] *= (1 + np.random.uniform(-0.1, 0.1))
        random_record['ai_workload'] *= (1 + np.random.uniform(-0.05, 0.05))
        
        # Upload to Supabase
        try:
            db_manager.supabase.table('cloud_emissions').insert(random_record).execute()
            print(f"Uploaded new data point at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"Error uploading data: {e}")
            
        time.sleep(5)  # Wait 5 seconds between updates

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--simulate', action='store_true', help='Run with simulated data')
    args = parser.parse_args()
    
    if args.simulate:
        print("Starting simulation mode...")
        simulate_real_time_data()
    else:
        print("Starting real-time monitoring...")
        monitor = RealtimeEmissionMonitor()
        monitor.start_realtime_monitoring() 
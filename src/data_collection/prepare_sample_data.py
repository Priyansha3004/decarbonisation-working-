import pandas as pd
import numpy as np
from pathlib import Path

def create_sample_device_data():
    """Create sample device energy consumption data"""
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='H')
    devices = ['laptop', 'desktop', 'server', 'mobile']
    
    data = []
    for device in devices:
        # Generate random usage patterns
        base_consumption = {
            'laptop': 50,
            'desktop': 100,
            'server': 400,
            'mobile': 10
        }[device]
        
        for date in dates:
            # Add daily and seasonal patterns
            hour_factor = 1 + np.sin(date.hour * np.pi / 12) * 0.5
            month_factor = 1 + np.sin(date.month * np.pi / 6) * 0.3
            
            consumption = base_consumption * hour_factor * month_factor
            consumption += np.random.normal(0, base_consumption * 0.1)
            
            data.append({
                'timestamp': date,
                'device_type': device,
                'energy_consumption_wh': max(0, consumption),
                'active_time_minutes': np.random.randint(0, 60)
            })
    
    return pd.DataFrame(data)

def create_sample_internet_data():
    """Create sample internet usage data"""
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='H')
    activities = ['streaming', 'browsing', 'download', 'video_call']
    
    data = []
    for activity in activities:
        base_data = {
            'streaming': {'data': 2000, 'energy': 0.2},
            'browsing': {'data': 100, 'energy': 0.02},
            'download': {'data': 500, 'energy': 0.05},
            'video_call': {'data': 800, 'energy': 0.08}
        }[activity]
        
        for date in dates:
            # Add usage patterns
            hour_factor = 1 + np.sin(date.hour * np.pi / 12) * 0.5
            
            data.append({
                'timestamp': date,
                'activity': activity,
                'data_transfer_mb': base_data['data'] * hour_factor * np.random.uniform(0.8, 1.2),
                'energy_consumption_wh': base_data['energy'] * hour_factor * np.random.uniform(0.8, 1.2)
            })
    
    return pd.DataFrame(data)

def main():
    # Create data directory
    data_dir = Path('data/raw')
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate and save device data
    device_df = create_sample_device_data()
    device_df.to_csv(data_dir / 'device_energy_data.csv', index=False)
    
    # Generate and save internet usage data
    internet_df = create_sample_internet_data()
    internet_df.to_csv(data_dir / 'internet_usage_data.csv', index=False)
    
    print("Sample data files created successfully!")
    print(f"Device data shape: {device_df.shape}")
    print(f"Internet data shape: {internet_df.shape}")

if __name__ == "__main__":
    main() 
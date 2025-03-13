from api_collector import CarbonDataCollector

def test_data_collection():
    collector = CarbonDataCollector()
    
    # Collect public data
    carbon_data = collector.collect_github_carbon_data()
    energy_data = collector.collect_energy_data()
    
    # Generate sample cloud data
    cloud_data = collector.generate_sample_cloud_data()
    
    # Read local CSV files
    device_data = collector.collect_local_csv_data('data/raw/device_energy_data.csv')
    internet_data = collector.collect_local_csv_data('data/raw/internet_usage_data.csv')
    
    print("Data collection complete!")
    print(f"Carbon data records: {len(carbon_data)}")
    print(f"Energy data records: {len(energy_data)}")
    print(f"Cloud data records: {len(cloud_data)}")
    print(f"Device data records: {len(device_data)}")
    print(f"Internet data records: {len(internet_data)}")

if __name__ == "__main__":
    test_data_collection() 
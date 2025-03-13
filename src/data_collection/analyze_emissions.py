from data_center_collector import DataCenterCollector
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_data_centers():
    collector = DataCenterCollector()
    
    # Load and analyze data
    provider_analysis = collector.analyze_by_provider()
    efficiency_metrics = collector.calculate_efficiency_metrics()
    ai_impact = collector.get_ai_workload_impact()
    
    # Print analysis results
    print("\n=== Cloud Provider Analysis ===")
    print(provider_analysis)
    
    print("\n=== Efficiency Metrics ===")
    print(efficiency_metrics)
    
    print("\n=== AI Workload Impact ===")
    print(ai_impact)
    
    # Create visualizations
    plt.figure(figsize=(12, 6))
    
    # Emissions by Provider
    plt.subplot(1, 2, 1)
    provider_analysis['Total Emissions (kg CO₂e)'].plot(kind='bar')
    plt.title('Total Emissions by Provider')
    plt.xticks(rotation=45)
    
    # AI Workload vs Energy Consumption
    plt.subplot(1, 2, 2)
    sns.scatterplot(data=collector.load_data_center_emissions(), 
                    x='AI Workload (%)', 
                    y='Energy Consumption (MWh)',
                    hue='Cloud Service Provider')
    plt.title('AI Workload vs Energy Consumption')
    
    plt.tight_layout()
    plt.savefig('data_center_analysis.png')
    plt.close()

if __name__ == "__main__":
    analyze_data_centers() 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

class CloudEmissionVisualizer:
    def __init__(self):
        self.data = pd.read_csv('data/raw/Enhanced_Data_Center_Emissions_Database.csv')
        # Set style for research-quality plots
        plt.style.use('default')
        self.colors = ['#2ecc71', '#3498db', '#e74c3c', '#f1c40f']
        
    def create_emission_distribution(self):
        """Create distribution analysis of emissions"""
        plt.figure(figsize=(15, 8))
        
        # Main emission distribution
        plt.subplot(1, 2, 1)
        sns.boxplot(x='Cloud Service Provider', 
                   y='Total Emissions (kg CO₂e)',
                   data=self.data,
                   palette=self.colors)
        plt.title('Distribution of Carbon Emissions by Provider', fontsize=12, pad=20)
        plt.xticks(rotation=45)
        plt.ylabel('Carbon Emissions (kg CO₂e)', fontsize=10)
        
        # Density plot
        plt.subplot(1, 2, 2)
        for idx, provider in enumerate(self.data['Cloud Service Provider'].unique()):
            provider_data = self.data[self.data['Cloud Service Provider'] == provider]
            sns.kdeplot(data=provider_data['Total Emissions (kg CO₂e)'],
                       label=provider,
                       color=self.colors[idx % len(self.colors)])
        plt.title('Emission Density Distribution', fontsize=12, pad=20)
        plt.xlabel('Carbon Emissions (kg CO₂e)', fontsize=10)
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('figures/emission_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()

    def create_ai_impact_analysis(self):
        """Analyze AI workload impact on emissions"""
        plt.figure(figsize=(15, 8))
        
        # Scatter plot with regression
        plt.subplot(1, 2, 1)
        sns.regplot(data=self.data,
                   x='AI Workload (%)',
                   y='Total Emissions (kg CO₂e)',
                   scatter_kws={'alpha':0.5},
                   line_kws={'color': 'red'})
        plt.title('AI Workload vs Emissions\nwith Regression Line', fontsize=12, pad=20)
        
        # Grouped bar chart
        plt.subplot(1, 2, 2)
        ai_groups = pd.qcut(self.data['AI Workload (%)'], 4, labels=['Low', 'Medium', 'High', 'Very High'])
        grouped_emissions = self.data.groupby([ai_groups, 'Cloud Service Provider'])['Total Emissions (kg CO₂e)'].mean().unstack()
        grouped_emissions.plot(kind='bar', width=0.8)
        plt.title('Average Emissions by AI Workload Category', fontsize=12, pad=20)
        plt.xticks(rotation=45)
        plt.legend(title='Provider')
        
        plt.tight_layout()
        plt.savefig('figures/ai_impact_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()

    def create_renewable_impact_visualization(self):
        """Visualize impact of renewable energy on emissions"""
        plt.figure(figsize=(15, 8))
        
        # Scatter plot with size representing total emissions
        plt.subplot(1, 2, 1)
        sns.scatterplot(data=self.data,
                       x='Renewable Energy Usage (%)',
                       y='Total Emissions (kg CO₂e)',
                       size='Energy Consumption (MWh)',
                       hue='Cloud Service Provider',
                       sizes=(100, 1000),
                       alpha=0.6)
        plt.title('Renewable Energy vs Emissions\nSize = Energy Consumption', fontsize=12, pad=20)
        
        # Heatmap of correlations
        plt.subplot(1, 2, 2)
        correlation_vars = ['Total Emissions (kg CO₂e)', 'Renewable Energy Usage (%)', 
                          'Energy Consumption (MWh)', 'AI Workload (%)']
        correlation_matrix = self.data[correlation_vars].corr()
        sns.heatmap(correlation_matrix, 
                   annot=True, 
                   cmap='RdYlGn_r',
                   center=0,
                   vmin=-1, 
                   vmax=1)
        plt.title('Correlation Matrix of Key Metrics', fontsize=12, pad=20)
        
        plt.tight_layout()
        plt.savefig('figures/renewable_impact.png', dpi=300, bbox_inches='tight')
        plt.close()

    def create_geographical_analysis(self):
        """Analyze emissions by geographical location"""
        plt.figure(figsize=(15, 8))
        
        # Emissions by location
        plt.subplot(1, 2, 1)
        location_emissions = self.data.groupby('Location')['Total Emissions (kg CO₂e)'].mean().sort_values(ascending=True)
        location_emissions.plot(kind='barh', color=self.colors)
        plt.title('Average Emissions by Location', fontsize=12, pad=20)
        plt.xlabel('Carbon Emissions (kg CO₂e)', fontsize=10)
        
        # Provider distribution by location
        plt.subplot(1, 2, 2)
        location_provider = pd.crosstab(self.data['Location'], self.data['Cloud Service Provider'])
        location_provider.plot(kind='bar', stacked=True)
        plt.title('Cloud Provider Distribution by Location', fontsize=12, pad=20)
        plt.xticks(rotation=45)
        plt.legend(title='Provider')
        
        plt.tight_layout()
        plt.savefig('figures/geographical_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()

    def create_efficiency_metrics(self):
        """Visualize efficiency metrics"""
        plt.figure(figsize=(15, 12))
        
        # PUE distribution
        plt.subplot(2, 2, 1)
        sns.violinplot(x='Cloud Service Provider', 
                      y='PUE (Power Usage Effectiveness)',
                      data=self.data,
                      palette=self.colors)
        plt.title('PUE Distribution by Provider', fontsize=12, pad=20)
        plt.xticks(rotation=45)
        
        # Emissions per MWh
        plt.subplot(2, 2, 2)
        self.data['Emissions_per_MWh'] = self.data['Total Emissions (kg CO₂e)'] / self.data['Energy Consumption (MWh)']
        sns.barplot(x='Cloud Service Provider',
                   y='Emissions_per_MWh',
                   data=self.data,
                   palette=self.colors)
        plt.title('Emissions Efficiency (kg CO₂e/MWh)', fontsize=12, pad=20)
        plt.xticks(rotation=45)
        
        # Renewable vs Non-renewable
        plt.subplot(2, 2, (3, 4))
        providers = self.data['Cloud Service Provider'].unique()
        renewable = self.data.groupby('Cloud Service Provider')['Renewable Energy Usage (%)'].mean()
        non_renewable = 100 - renewable
        
        x = np.arange(len(providers))
        width = 0.35
        
        plt.bar(x, renewable, width, label='Renewable', color='#2ecc71')
        plt.bar(x, non_renewable, width, bottom=renewable, label='Non-Renewable', color='#e74c3c')
        plt.xlabel('Cloud Service Provider')
        plt.ylabel('Percentage')
        plt.title('Renewable vs Non-Renewable Energy Usage', fontsize=12, pad=20)
        plt.xticks(x, providers, rotation=45)
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('figures/efficiency_metrics.png', dpi=300, bbox_inches='tight')
        plt.close()

def main():
    # Create directory for figures
    import os
    os.makedirs('figures', exist_ok=True)
    
    visualizer = CloudEmissionVisualizer()
    
    print("Generating research-quality visualizations...")
    visualizer.create_emission_distribution()
    print("✓ Created emission distribution analysis")
    
    visualizer.create_ai_impact_analysis()
    print("✓ Created AI impact analysis")
    
    visualizer.create_renewable_impact_visualization()
    print("✓ Created renewable energy impact visualization")
    
    visualizer.create_geographical_analysis()
    print("✓ Created geographical analysis")
    
    visualizer.create_efficiency_metrics()
    print("✓ Created efficiency metrics visualization")
    
    print("\nAll visualizations have been saved in the 'figures' directory.")
    print("Each figure is saved in high resolution (300 DPI) suitable for research papers.")

if __name__ == "__main__":
    main() 
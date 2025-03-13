import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

class CloudCarbonAnalyzer:
    def __init__(self):
        self.data = pd.read_csv('data/raw/Enhanced_Data_Center_Emissions_Database.csv')
        self.model = None
        
    def prepare_features(self):
        """Prepare features for carbon emission prediction"""
        # Select relevant features for carbon emissions
        features = ['Energy Consumption (MWh)', 'AI Workload (%)', 
                   'Renewable Energy Usage (%)', 'PUE (Power Usage Effectiveness)']
        
        X = self.data[features]
        y = self.data['Total Emissions (kg CO₂e)']
        
        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train_emission_model(self):
        """Train AI model to predict carbon emissions"""
        X_train, X_test, y_train, y_test = self.prepare_features()
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = self.model.predict(X_test_scaled)
        
        # Calculate metrics
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        return {
            'mse': mse,
            'rmse': np.sqrt(mse),
            'r2': r2,
            'feature_importance': dict(zip(X_train.columns, 
                                         self.model.feature_importances_))
        }

    def analyze_cloud_emissions(self):
        """Analyze carbon emissions by cloud provider"""
        # Calculate total emissions by provider
        provider_emissions = self.data.groupby('Cloud Service Provider').agg({
            'Total Emissions (kg CO₂e)': 'sum',
            'AI Workload (%)': 'mean',
            'Renewable Energy Usage (%)': 'mean'
        }).round(2)
        
        return provider_emissions

    def visualize_emissions(self):
        """Create visualizations for carbon emissions analysis"""
        plt.style.use('seaborn')
        fig = plt.figure(figsize=(15, 10))

        # 1. Cloud Provider Emissions
        plt.subplot(2, 2, 1)
        provider_emissions = self.data.groupby('Cloud Service Provider')['Total Emissions (kg CO₂e)'].sum()
        provider_emissions.plot(kind='bar')
        plt.title('Total Carbon Emissions by Cloud Provider')
        plt.ylabel('Carbon Emissions (kg CO₂e)')
        plt.xticks(rotation=45)

        # 2. AI Workload vs Emissions
        plt.subplot(2, 2, 2)
        sns.scatterplot(data=self.data, 
                       x='AI Workload (%)', 
                       y='Total Emissions (kg CO₂e)',
                       hue='Cloud Service Provider',
                       size='Energy Consumption (MWh)',
                       sizes=(50, 200))
        plt.title('AI Workload vs Carbon Emissions')

        # 3. Renewable Energy Impact
        plt.subplot(2, 2, 3)
        sns.scatterplot(data=self.data,
                       x='Renewable Energy Usage (%)',
                       y='Total Emissions (kg CO₂e)',
                       hue='Cloud Service Provider')
        plt.title('Renewable Energy Usage vs Emissions')

        # 4. Feature Importance from AI Model
        if self.model:
            plt.subplot(2, 2, 4)
            importance = pd.Series(self.model.feature_importances_,
                                 index=['Energy', 'AI Load', 'Renewable', 'PUE'])
            importance.plot(kind='bar')
            plt.title('Feature Importance in Emission Prediction')
            plt.xticks(rotation=45)

        plt.tight_layout()
        plt.savefig('cloud_carbon_analysis.png')
        plt.close()

def main():
    analyzer = CloudCarbonAnalyzer()
    
    # Train AI model
    print("\n=== AI Model Performance ===")
    metrics = analyzer.train_emission_model()
    print(f"RMSE: {metrics['rmse']:.2f} kg CO₂e")
    print(f"R² Score: {metrics['r2']:.2f}")
    print("\nFeature Importance:")
    for feature, importance in metrics['feature_importance'].items():
        print(f"{feature}: {importance:.3f}")

    # Analyze cloud provider emissions
    print("\n=== Cloud Provider Carbon Analysis ===")
    provider_analysis = analyzer.analyze_cloud_emissions()
    print(provider_analysis)

    # Generate visualizations
    analyzer.visualize_emissions()
    print("\nVisualizations saved as 'cloud_carbon_analysis.png'")

if __name__ == "__main__":
    main() 
import streamlit as st
import pandas as pd
from realtime_monitor import RealtimeEmissionMonitor
import time

def create_dashboard():
    st.set_page_config(page_title="Cloud Carbon Emissions Monitor", layout="wide")
    st.title("Real-time Cloud Carbon Emissions Dashboard")
    
    monitor = RealtimeEmissionMonitor()
    
    # Create placeholder for real-time updates
    metrics_placeholder = st.empty()
    chart_placeholder = st.empty()
    
    while True:
        # Get latest data
        emissions_data = monitor.supabase.table('cloud_emissions').select('*').execute()
        df = pd.DataFrame(emissions_data.data)
        
        with metrics_placeholder.container():
            # Display key metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Emissions",
                    f"{df['total_emissions'].sum():,.0f} kg CO₂e",
                    f"{df['total_emissions'].diff().mean():+.1f} kg"
                )
                
            with col2:
                st.metric(
                    "Average AI Workload",
                    f"{df['ai_workload'].mean():.1f}%",
                    f"{df['ai_workload'].diff().mean():+.1f}%"
                )
                
            with col3:
                st.metric(
                    "Renewable Energy Usage",
                    f"{df['renewable_energy_usage'].mean():.1f}%",
                    f"{df['renewable_energy_usage'].diff().mean():+.1f}%"
                )
        
        with chart_placeholder.container():
            # Create real-time charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.line_chart(df.set_index('uploaded_at')['total_emissions'])
                st.bar_chart(df.groupby('cloud_service_provider')['total_emissions'].sum())
                
            with col2:
                st.scatter_chart(
                    data=df,
                    x='ai_workload',
                    y='total_emissions',
                    color='cloud_service_provider'
                )
        
        time.sleep(5)  # Update every 5 seconds

if __name__ == "__main__":
    create_dashboard() 
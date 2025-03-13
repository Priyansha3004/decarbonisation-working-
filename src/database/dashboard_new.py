# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import numpy as np
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt

# Add location coordinates
LOCATION_COORDS = {
    'California': {'lat': 36.7783, 'lon': -119.4179},
    'Virginia': {'lat': 37.7693, 'lon': -78.1700},
    'London': {'lat': 51.5074, 'lon': -0.1278},
    'Sydney': {'lat': -33.8688, 'lon': 151.2093},
    'Mumbai': {'lat': 19.0760, 'lon': 72.8777},
    'Dublin': {'lat': 53.3498, 'lon': -6.2603},
    'Singapore': {'lat': 1.3521, 'lon': 103.8198},
    'Berlin': {'lat': 52.5200, 'lon': 13.4050},
    'Tokyo': {'lat': 35.6762, 'lon': 139.6503},
    'Toronto': {'lat': 43.6532, 'lon': -79.3832}
}

def load_data():
    """Load and prepare data"""
    try:
        df = pd.read_csv('data/raw/Enhanced_Data_Center_Emissions_Database.csv')
        # Calculate additional metrics
        df['Energy Efficiency'] = df['Energy Consumption (MWh)'] / df['Total Emissions (kg CO₂e)']
        df['Sustainability Score'] = (df['Renewable Energy Usage (%)'] / 100 * 0.4 + 
                                    (2.0 - df['PUE (Power Usage Effectiveness)']) / 1.0 * 0.3 +
                                    df['Energy Efficiency'] / df['Energy Efficiency'].max() * 0.3)
        
        # Add coordinates
        df['Latitude'] = df['Location'].map(lambda x: LOCATION_COORDS[x]['lat'])
        df['Longitude'] = df['Location'].map(lambda x: LOCATION_COORDS[x]['lon'])
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def create_correlation_heatmap(df):
    """Create a correlation heatmap"""
    numeric_cols = ['Energy Consumption (MWh)', 'Total Emissions (kg CO₂e)', 
                   'Renewable Energy Usage (%)', 'PUE (Power Usage Effectiveness)', 
                   'AI Workload (%)', 'Energy Efficiency', 'Sustainability Score']
    corr = df[numeric_cols].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr,
        x=numeric_cols,
        y=numeric_cols,
        colorscale='RdBu',
        zmin=-1,
        zmax=1
    ))
    fig.update_layout(
        title='Correlation Matrix of Key Metrics',
        height=600
    )
    return fig

def create_3d_scatter(df):
    """Create 3D scatter plot"""
    fig = px.scatter_3d(
        df,
        x='Energy Consumption (MWh)',
        y='Total Emissions (kg CO₂e)',
        z='Renewable Energy Usage (%)',
        color='Cloud Service Provider',
        size='AI Workload (%)',
        hover_data=['Location', 'PUE (Power Usage Effectiveness)'],
        title='3D Analysis of Energy, Emissions, and Renewable Usage'
    )
    fig.update_layout(height=700)
    return fig

def create_radar_chart(df):
    """Create radar chart for provider comparison"""
    providers = df['Cloud Service Provider'].unique()
    metrics = ['Energy Efficiency', 'Renewable Energy Usage (%)', 
              'PUE (Power Usage Effectiveness)', 'AI Workload (%)',
              'Sustainability Score']
    
    fig = go.Figure()
    for provider in providers:
        provider_data = df[df['Cloud Service Provider'] == provider]
        values = [
            provider_data['Energy Efficiency'].mean() / df['Energy Efficiency'].max(),
            provider_data['Renewable Energy Usage (%)'].mean() / 100,
            (2 - provider_data['PUE (Power Usage Effectiveness)'].mean()) / 1,
            provider_data['AI Workload (%)'].mean() / 100,
            provider_data['Sustainability Score'].mean()
        ]
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=metrics,
            name=provider
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        title='Provider Performance Comparison'
    )
    return fig

def create_globe_visualization(df):
    """Create an interactive 3D globe visualization"""
    
    # Create hover text
    df['hover_text'] = df.apply(lambda row: f"""
        <b>{row['Location']}</b><br>
        Provider: {row['Cloud Service Provider']}<br>
        Emissions: {row['Total Emissions (kg CO₂e)']:,.0f} kg CO₂e<br>
        Renewable: {row['Renewable Energy Usage (%)']:.1f}%<br>
        PUE: {row['PUE (Power Usage Effectiveness)']:.2f}<br>
        AI Workload: {row['AI Workload (%)']}%
    """, axis=1)

    # Create the globe
    fig = go.Figure()

    # Add data centers as points
    fig.add_trace(go.Scattergeo(
        lon=df['Longitude'],
        lat=df['Latitude'],
        text=df['hover_text'],
        mode='markers',
        marker=dict(
            size=df['Total Emissions (kg CO₂e)'] / df['Total Emissions (kg CO₂e)'].max() * 50,
            color=df['Sustainability Score'],
            colorscale='Viridis',
            showscale=True,
            colorbar_title='Sustainability Score'
        ),
        hoverinfo='text',
        name='Data Centers'
    ))

    # Add connecting lines between data centers
    for i in range(len(df)-1):
        fig.add_trace(go.Scattergeo(
            lon=[df.iloc[i]['Longitude'], df.iloc[i+1]['Longitude']],
            lat=[df.iloc[i]['Latitude'], df.iloc[i+1]['Latitude']],
            mode='lines',
            line=dict(width=1, color='rgba(100, 100, 100, 0.2)'),
            showlegend=False
        ))

    # Update layout for globe view
    fig.update_layout(
        title='Global Data Center Network',
        showlegend=True,
        geo=dict(
            projection_type='orthographic',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
            showocean=True,
            oceancolor='rgb(230, 230, 250)',
            showlakes=True,
            lakecolor='rgb(230, 230, 250)',
            showcountries=True,
            resolution=50,
            showcoastlines=True,
            coastlinecolor='rgb(150, 150, 150)',
        ),
        height=800,
        updatemenus=[{
            'buttons': [
                {
                    'args': [None, {'frame': {'duration': 500, 'redraw': True},
                                  'fromcurrent': True,
                                  'transition': {'duration': 300, 'easing': 'quadratic-in-out'}}],
                    'label': 'Rotate View',
                    'method': 'animate'
                }
            ],
            'type': 'buttons',
            'showactive': False,
            'x': 0.1,
            'y': 0.1,
        }]
    )

    # Add frames for rotation animation
    frames = []
    for lon in range(0, 361, 10):
        frame = go.Frame(
            layout=dict(
                geo_center_lon=lon,
                geo_projection_rotation_lon=lon
            )
        )
        frames.append(frame)
    fig.frames = frames

    return fig

def create_trend_analysis(df):
    """Create time-based trend analysis"""
    # Simulate monthly data (since we don't have actual time series)
    dates = pd.date_range(start='2024-01-01', periods=len(df), freq='M')
    df_trend = df.copy()
    df_trend['Date'] = dates
    
    fig = go.Figure()
    
    # Add emissions trend
    fig.add_trace(go.Scatter(
        x=df_trend['Date'],
        y=df_trend['Total Emissions (kg CO₂e)'],
        name='Emissions',
        line=dict(color='#1E88E5')
    ))
    
    # Add renewable usage trend
    fig.add_trace(go.Scatter(
        x=df_trend['Date'],
        y=df_trend['Renewable Energy Usage (%)'],
        name='Renewable Usage',
        line=dict(color='#43A047'),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='Emissions and Renewable Usage Trends',
        xaxis_title='Date',
        yaxis_title='Emissions (kg CO₂e)',
        yaxis2=dict(
            title='Renewable Usage (%)',
            overlaying='y',
            side='right'
        ),
        height=400,
        showlegend=True
    )
    
    return fig

def generate_ai_insights(df):
    """Generate AI-powered insights from the data"""
    insights = []
    
    # Efficiency Analysis
    top_efficient = df.nlargest(1, 'Energy Efficiency')
    insights.append({
        'category': 'Efficiency',
        'title': 'Most Efficient Data Center',
        'description': f"The {top_efficient['Location'].iloc[0]} facility operated by {top_efficient['Cloud Service Provider'].iloc[0]} "
                      f"shows the highest efficiency at {top_efficient['Energy Efficiency'].iloc[0]:.2f} MWh/kg CO₂e",
        'impact': 'high'
    })
    
    # Renewable Usage Patterns
    avg_renewable = df['Renewable Energy Usage (%)'].mean()
    high_renewable = df[df['Renewable Energy Usage (%)'] > avg_renewable]
    insights.append({
        'category': 'Renewable Energy',
        'title': 'Renewable Energy Leaders',
        'description': f"{len(high_renewable)} facilities exceed the average renewable usage of {avg_renewable:.1f}%",
        'impact': 'medium'
    })
    
    # Emissions Hotspots
    high_emissions = df[df['Total Emissions (kg CO₂e)'] > df['Total Emissions (kg CO₂e)'].quantile(0.75)]
    insights.append({
        'category': 'Emissions',
        'title': 'Emissions Hotspots Identified',
        'description': f"Found {len(high_emissions)} facilities with significantly high emissions that need attention",
        'impact': 'high'
    })
    
    return insights

def check_alerts(df):
    """Check for alert conditions in the data"""
    alerts = []
    
    # Check for high emissions
    emissions_threshold = df['Total Emissions (kg CO₂e)'].mean() * 1.5
    high_emitters = df[df['Total Emissions (kg CO₂e)'] > emissions_threshold]
    if not high_emitters.empty:
        alerts.append({
            'level': 'critical',
            'message': f"⚠️ {len(high_emitters)} facilities exceed emissions threshold",
            'details': f"Average excess: {(high_emitters['Total Emissions (kg CO₂e)'].mean() - emissions_threshold):,.0f} kg CO₂e"
        })
    
    # Check for low renewable usage
    low_renewable = df[df['Renewable Energy Usage (%)'] < 30]
    if not low_renewable.empty:
        alerts.append({
            'level': 'warning',
            'message': f"📉 {len(low_renewable)} facilities below 30% renewable usage",
            'details': "Consider increasing renewable energy sources"
        })
    
    # Check for PUE efficiency
    inefficient = df[df['PUE (Power Usage Effectiveness)'] > 1.8]
    if not inefficient.empty:
        alerts.append({
            'level': 'info',
            'message': f"ℹ️ {len(inefficient)} facilities have PUE > 1.8",
            'details': "Optimization opportunity identified"
        })
    
    return alerts

def create_dashboard():
    st.set_page_config(page_title="Cloud Carbon Analytics", layout="wide", page_icon="🌍")
    
    # Professional theme configurations - Moved to the beginning
    theme_configs = {
        "Light": {
            "bg": "#ffffff",
            "text": "#1a1f36",
            "accent": "#0066cc",
            "secondary": "#6b7280",
            "success": "#059669",
            "warning": "#d97706",
            "error": "#dc2626",
            "surface": "#f3f4f6",
            "card": "#ffffff",
            "border": "#e5e7eb",
            "hover": "#f9fafb",
            "chart": "plotly",
            "muted": "#9ca3af"
        },
        "Dark": {
            "bg": "#0a0a0a",
            "text": "#f3f4f6",
            "accent": "#3b82f6",
            "secondary": "#64748b",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444",
            "surface": "#18181b",
            "card": "#27272a",
            "border": "#3f3f46",
            "hover": "#3f3f46",
            "chart": "plotly_dark",
            "muted": "#71717a"
        },
        "Corporate": {
            "bg": "#f8fafc",
            "text": "#0f172a",
            "accent": "#1e40af",
            "secondary": "#475569",
            "success": "#15803d",
            "warning": "#b45309",
            "error": "#b91c1c",
            "surface": "#ffffff",
            "card": "#ffffff",
            "border": "#e2e8f0",
            "hover": "#f1f5f9",
            "chart": "plotly",
            "muted": "#64748b"
        }
    }
    
    # Theme selection - Moved up before styling is applied
    theme = "Light"  # Default theme
    
    # Header with custom styling
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5em;
            color: #1E88E5;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
        }
        .version-info {
            font-size: 0.8em;
            color: #666;
            text-align: right;
            padding-right: 20px;
        }
        .quick-nav {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        </style>
        <h1 class='main-header'>Advanced Cloud Carbon Analytics</h1>
        <div class='version-info'>v2.0 | Enterprise Edition</div>
    """, unsafe_allow_html=True)
    
    # Add quick navigation
    st.markdown("""
        <div class='quick-nav'>
            <strong>Quick Navigation:</strong> Use the tabs below to explore different aspects of cloud carbon analytics. 
            For detailed filtering, use the controls in the sidebar.
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <style>
        .stMetric .metric-label { font-size: 1.2em !important; }
        .stMetric .metric-value { font-size: 2em !important; }
        </style>
    """, unsafe_allow_html=True)

    # Load data
    df = load_data()
    if df is None:
        return

    # Sidebar with enhanced filters
    st.sidebar.title("Analytics Controls")
    
    # Provider filter
    providers = st.sidebar.multiselect(
        "Select Cloud Providers",
        df['Cloud Service Provider'].unique(),
        default=df['Cloud Service Provider'].unique()
    )
    
    # Location filter
    locations = st.sidebar.multiselect(
        "Select Locations",
        df['Location'].unique(),
        default=df['Location'].unique()
    )
    
    # Advanced filters
    st.sidebar.markdown("---")
    st.sidebar.subheader("Advanced Filters")
    min_renewable = st.sidebar.slider("Minimum Renewable %", 0, 100, 0)
    max_pue = st.sidebar.slider("Maximum PUE", 1.0, 2.0, 2.0)

    # Filter data
    df_filtered = df[
        (df['Cloud Service Provider'].isin(providers)) &
        (df['Location'].isin(locations)) &
        (df['Renewable Energy Usage (%)'] >= min_renewable) &
        (df['PUE (Power Usage Effectiveness)'] <= max_pue)
    ]

    # Main metrics with enhanced styling
    st.markdown("### Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Emissions",
            f"{df_filtered['Total Emissions (kg CO₂e)'].sum():,.0f} kg",
            f"Across {len(df_filtered)} facilities"
        )
    
    with col2:
        st.metric(
            "Avg Renewable Usage",
            f"{df_filtered['Renewable Energy Usage (%)'].mean():.1f}%",
            f"{df_filtered['Renewable Energy Usage (%)'].mean() - df['Renewable Energy Usage (%)'].mean():.1f}% vs All"
        )
    
    with col3:
        st.metric(
            "Sustainability Score",
            f"{df_filtered['Sustainability Score'].mean():.2f}",
            "Overall Performance"
        )
    
    with col4:
        st.metric(
            "Energy Efficiency",
            f"{df_filtered['Energy Efficiency'].mean():.2f}",
            "MWh/kg CO₂e"
        )

    # Create tabs for different analyses
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Performance Analysis",
        "Correlations",
        "Provider Comparison",
        "Geographic Analysis",
        "🌍 Interactive Globe",
        "Trend Analysis",
        "AI Insights"
    ])

    with tab1:
        st.markdown("### Performance Metrics")
        col1, col2 = st.columns(2)
        
        with col1:
            # Enhanced emissions by provider
            fig = px.bar(
                df_filtered.groupby('Cloud Service Provider').agg({
                    'Total Emissions (kg CO₂e)': 'sum',
                    'Energy Consumption (MWh)': 'sum'
                }).reset_index(),
                x='Cloud Service Provider',
                y=['Total Emissions (kg CO₂e)', 'Energy Consumption (MWh)'],
                title='Emissions and Energy by Provider',
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Efficiency scatter plot
            fig = px.scatter(
                df_filtered,
                x='Energy Efficiency',
                y='Sustainability Score',
                color='Cloud Service Provider',
                size='AI Workload (%)',
                hover_data=['Location'],
                title='Efficiency vs Sustainability'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 3D visualization
        st.markdown("### 3D Performance Visualization")
        st.plotly_chart(create_3d_scatter(df_filtered), use_container_width=True)

    with tab2:
        st.markdown("### Correlation Analysis")
        # Correlation heatmap
        st.plotly_chart(create_correlation_heatmap(df_filtered), use_container_width=True)
        
        # Trend analysis
        st.markdown("### Trend Analysis")
        fig = px.scatter(
            df_filtered,
            x='AI Workload (%)',
            y='Total Emissions (kg CO₂e)',
            color='Cloud Service Provider',
            trendline="ols",
            title='AI Workload vs Emissions Trend'
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.markdown("### Provider Performance Comparison")
        # Radar chart
        st.plotly_chart(create_radar_chart(df_filtered), use_container_width=True)
        
        # Performance metrics table
        st.markdown("### Detailed Performance Metrics")
        metrics_df = df_filtered.groupby('Cloud Service Provider').agg({
            'Energy Efficiency': 'mean',
            'Renewable Energy Usage (%)': 'mean',
            'PUE (Power Usage Effectiveness)': 'mean',
            'AI Workload (%)': 'mean',
            'Sustainability Score': 'mean'
        }).round(2)
        st.dataframe(metrics_df, use_container_width=True)

    with tab4:
        st.markdown("### Geographic Distribution")
        col1, col2 = st.columns(2)
        
        with col1:
            # Location-based emissions
            location_emissions = df_filtered.groupby('Location').agg({
                'Total Emissions (kg CO₂e)': 'sum',
                'Energy Consumption (MWh)': 'sum'
            }).reset_index()
            
            fig = px.bar(
                location_emissions,
                x='Location',
                y='Total Emissions (kg CO₂e)',
                title='Emissions by Location',
                color='Total Emissions (kg CO₂e)',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                xaxis_tickangle=-45,
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Provider distribution by location
            provider_loc_count = df_filtered.groupby(['Location', 'Cloud Service Provider']).size().reset_index(name='count')
            fig = px.sunburst(
                provider_loc_count,
                path=['Location', 'Cloud Service Provider'],
                values='count',
                title='Provider Distribution by Location'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        # Location statistics
        st.markdown("### Location Performance Metrics")
        location_metrics = df_filtered.groupby('Location').agg({
            'Renewable Energy Usage (%)': 'mean',
            'PUE (Power Usage Effectiveness)': 'mean',
            'AI Workload (%)': 'mean',
            'Sustainability Score': 'mean'
        }).round(2)

        # Create heatmap using go.Figure
        fig = go.Figure(data=go.Heatmap(
            z=location_metrics.values.T,
            x=location_metrics.index,
            y=location_metrics.columns,
            colorscale='RdYlGn',
            text=location_metrics.values.T.round(2),
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False
        ))

        fig.update_layout(
            title='Location Performance Metrics Heatmap',
            height=400,
            yaxis={'title': 'Metrics', 'tickangle': 0},
            xaxis={'title': 'Location', 'tickangle': -45},
            margin={'t': 50, 'l': 200}
        )
        st.plotly_chart(fig, use_container_width=True)

        # Add a table view for detailed numbers
        st.markdown("### Detailed Metrics by Location")
        st.dataframe(
            location_metrics.style.background_gradient(cmap='RdYlGn', axis=None),
            use_container_width=True
        )

    with tab5:
        st.markdown("### Interactive Globe Visualization")
        st.markdown("""
        Click on any data center to view detailed information. Use the rotation control to view the globe from different angles.
        The size of each point represents relative emissions, and the color indicates the sustainability score.
        """)
        
        # Add globe visualization
        globe_fig = create_globe_visualization(df_filtered)
        st.plotly_chart(globe_fig, use_container_width=True)
        
        # Add detailed metrics below the globe
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Regional Distribution")
            region_metrics = df_filtered.groupby('Location').agg({
                'Total Emissions (kg CO₂e)': 'sum',
                'Renewable Energy Usage (%)': 'mean',
                'Sustainability Score': 'mean'
            }).round(2)
            
            fig = px.scatter(
                region_metrics,
                x='Renewable Energy Usage (%)',
                y='Sustainability Score',
                size='Total Emissions (kg CO₂e)',
                hover_name=region_metrics.index,
                title='Regional Sustainability Overview'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Network Connectivity")
            st.markdown("""
            The lines connecting data centers represent the network of cloud infrastructure.
            Darker points indicate higher sustainability scores.
            """)
            
            # Add a summary table
            summary_df = pd.DataFrame({
                'Metric': ['Total Locations', 'Total Providers', 'Avg Sustainability Score', 'Total Emissions (tons CO₂e)'],
                'Value': [
                    len(df_filtered['Location'].unique()),
                    len(df_filtered['Cloud Service Provider'].unique()),
                    f"{df_filtered['Sustainability Score'].mean():.2f}",
                    f"{df_filtered['Total Emissions (kg CO₂e)'].sum() / 1000:,.1f}"
                ]
            })
            st.table(summary_df)

    with tab6:
        st.markdown("### Temporal Analysis")
        st.markdown("Track emissions and renewable usage trends over time")
        st.plotly_chart(create_trend_analysis(df_filtered), use_container_width=True)
        
        # Add forecast section
        st.markdown("### Projected Improvements")
        col1, col2 = st.columns(2)
        with col1:
            current_emissions = df_filtered['Total Emissions (kg CO₂e)'].sum()
            projected_reduction = current_emissions * 0.85  # Simulate 15% reduction
            st.metric(
                "Projected Annual Emissions",
                f"{projected_reduction:,.0f} kg",
                f"-{(current_emissions - projected_reduction) / current_emissions * 100:.1f}%"
            )
        with col2:
            current_renewable = df_filtered['Renewable Energy Usage (%)'].mean()
            projected_renewable = min(current_renewable * 1.2, 100)  # Simulate 20% increase
            st.metric(
                "Projected Renewable Usage",
                f"{projected_renewable:.1f}%",
                f"+{(projected_renewable - current_renewable):.1f}%"
            )

    with tab7:
        st.markdown("### 🤖 AI-Powered Insights")
        st.markdown("""
        Our AI analysis has identified the following key insights and recommendations 
        based on your current data center operations.
        """)
        
        insights = generate_ai_insights(df_filtered)
        
        for insight in insights:
            with st.expander(f"📊 {insight['title']}", expanded=True):
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"**Category:** {insight['category']}")
                    st.markdown(insight['description'])
                with col2:
                    impact_color = {
                        'high': '🔴',
                        'medium': '🟡',
                        'low': '🟢'
                    }
                    st.markdown(f"**Impact:** {impact_color[insight['impact']]}")
        
        # Add recommendations section
        st.markdown("### 📈 Optimization Recommendations")
        recommendations = [
            "Consider migrating high-emission workloads to locations with better renewable energy access",
            "Implement automated workload scheduling during peak renewable energy availability",
            "Focus on improving PUE in data centers with scores above 1.5",
            "Evaluate potential for renewable energy partnerships in high-emission regions"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")
            
        # Add predictive metrics
        st.markdown("### 🔮 Predictive Metrics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Predicted Monthly Savings",
                "23.5 tons CO₂e",
                "Based on current optimization trends"
            )
        
        with col2:
            st.metric(
                "Renewable Energy Potential",
                "85%",
                "+15% from current"
            )

    # Add export functionality in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Export Data")
    
    # Custom styling for export buttons
    st.markdown(f"""
        <style>
        /* Primary button (Download) */
        .stDownloadButton button {{
            background-color: {theme_configs[theme]["accent"]} !important;
            color: white !important;
            border: none !important;
            padding: 0.75rem 1rem !important;
            border-radius: 6px !important;
            width: 100% !important;
            font-weight: 500 !important;
            margin: 0.5rem 0 !important;
            transition: all 0.2s ease !important;
            cursor: pointer !important;
        }}
        
        .stDownloadButton button:hover {{
            background-color: {theme_configs[theme]["accent"] + "ee"} !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
        }}
        
        /* Secondary button (Generate Summary) */
        .stButton button {{
            background-color: {theme_configs[theme]["surface"]} !important;
            color: {theme_configs[theme]["accent"]} !important;
            border: 1px solid {theme_configs[theme]["accent"]} !important;
            padding: 0.75rem 1rem !important;
            border-radius: 6px !important;
            width: 100% !important;
            font-weight: 500 !important;
            margin: 0.5rem 0 !important;
            transition: all 0.2s ease !important;
            cursor: pointer !important;
        }}
        
        .stButton button:hover {{
            background-color: {theme_configs[theme]["accent"] + "11"} !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
        }}
        
        /* Fix button text color */
        .stDownloadButton button p {{
            color: white !important;
        }}
        
        .stButton button p {{
            color: {theme_configs[theme]["accent"]} !important;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    # CSV Download button
    csv = df_filtered.to_csv(index=False)
    st.sidebar.download_button(
        label="Download Full Report (CSV)",
        data=csv,
        file_name="cloud_carbon_analytics.csv",
        mime="text/csv",
        use_container_width=True,
        key="download_csv"
    )
    
    # Add some spacing
    st.sidebar.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    
    # Summary Report button
    if st.sidebar.button(
        "Generate Summary Report",
        use_container_width=True,
        key="summary_report"
    ):
        st.sidebar.markdown("### Summary Report")
        summary_stats = {
            'Total Facilities': len(df_filtered),
            'Total Emissions (tons CO₂e)': f"{df_filtered['Total Emissions (kg CO₂e)'].sum() / 1000:,.2f}",
            'Average Sustainability Score': f"{df_filtered['Sustainability Score'].mean():.2f}",
            'Top Performing Location': df_filtered.groupby('Location')['Sustainability Score'].mean().idxmax()
        }
        
        # Display summary stats in a more visually appealing way
        for key, value in summary_stats.items():
            st.sidebar.markdown(
                f"""
                <div style='
                    background-color: {theme_configs[theme]["surface"]};
                    border: 1px solid {theme_configs[theme]["border"]};
                    border-radius: 6px;
                    padding: 12px;
                    margin: 8px 0;
                '>
                    <div style='color: {theme_configs[theme]["secondary"]}; font-size: 0.9em;'>{key}</div>
                    <div style='color: {theme_configs[theme]["text"]}; font-size: 1.1em; font-weight: 500;'>{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Add theme customization in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Dashboard Settings")
    
    # Theme selection
    theme = st.sidebar.selectbox(
        "Color Theme",
        ["Light", "Dark", "Corporate"],
        key="theme_select"
    )
    
    # Apply professional theme styling
    st.markdown(f"""
        <style>
        /* Base styles */
        .stApp {{
            background-color: {theme_configs[theme]["bg"]};
            color: {theme_configs[theme]["text"]};
        }}
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 {{
            color: {theme_configs[theme]["text"]};
            font-weight: 600;
        }}
        
        p {{
            color: {theme_configs[theme]["secondary"]};
        }}
        
        /* Header styling */
        .main-header {{
            color: {theme_configs[theme]["accent"]};
            font-size: 2.5em;
            font-weight: 700;
            text-align: center;
            padding: 1.5rem;
            background: linear-gradient(90deg, {theme_configs[theme]["accent"] + "15"} 0%, transparent 100%);
            border-radius: 8px;
            margin-bottom: 2rem;
            border: 1px solid {theme_configs[theme]["border"]};
        }}
        
        /* Navigation */
        .quick-nav {{
            background-color: {theme_configs[theme]["surface"]};
            border: 1px solid {theme_configs[theme]["border"]};
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }}
        
        /* Metrics */
        .stMetric {{
            background-color: {theme_configs[theme]["card"]};
            border: 1px solid {theme_configs[theme]["border"]};
            border-radius: 8px;
            padding: 1.25rem;
            transition: all 0.2s ease;
        }}
        
        .stMetric:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }}
        
        .metric-label {{
            color: {theme_configs[theme]["secondary"]};
            font-size: 1rem;
            font-weight: 500;
        }}
        
        .metric-value {{
            color: {theme_configs[theme]["accent"]};
            font-size: 1.875rem;
            font-weight: 600;
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {theme_configs[theme]["surface"]};
            border-right: 1px solid {theme_configs[theme]["border"]};
        }}
        
        [data-testid="stSidebar"] [data-testid="stMarkdown"] {{
            color: {theme_configs[theme]["text"]};
        }}
        
        /* Buttons */
        .stButton button {{
            background-color: {theme_configs[theme]["accent"]};
            color: white;
            border: none;
            padding: 0.625rem 1.25rem;
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        
        .stButton button:hover {{
            background-color: {theme_configs[theme]["accent"] + "ee"};
            transform: translateY(-1px);
        }}
        
        /* Select boxes */
        .stSelectbox [data-baseweb="select"] {{
            background-color: {theme_configs[theme]["card"]};
            border: 1px solid {theme_configs[theme]["border"]};
            border-radius: 6px;
        }}
        
        .stSelectbox [data-baseweb="select"]:hover {{
            border-color: {theme_configs[theme]["accent"]};
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: {theme_configs[theme]["surface"]};
            border-bottom: 1px solid {theme_configs[theme]["border"]};
            gap: 0.5rem;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            color: {theme_configs[theme]["secondary"]};
            border-radius: 6px 6px 0 0;
            padding: 0.75rem 1rem;
            font-weight: 500;
        }}
        
        .stTabs [aria-selected="true"] {{
            color: {theme_configs[theme]["accent"]};
            border-bottom: 2px solid {theme_configs[theme]["accent"]};
            background-color: {theme_configs[theme]["accent"] + "10"};
        }}
        
        /* DataFrames */
        .stDataFrame {{
            background-color: {theme_configs[theme]["card"]};
            border: 1px solid {theme_configs[theme]["border"]};
            border-radius: 8px;
        }}
        
        .stDataFrame td, .stDataFrame th {{
            color: {theme_configs[theme]["text"]};
            border-color: {theme_configs[theme]["border"]};
        }}
        
        .stDataFrame tr:hover td {{
            background-color: {theme_configs[theme]["hover"]};
        }}
        
        /* Plotly charts */
        .js-plotly-plot {{
            background-color: {theme_configs[theme]["card"]};
            border: 1px solid {theme_configs[theme]["border"]};
            border-radius: 8px;
            padding: 1rem;
        }}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {theme_configs[theme]["surface"]};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {theme_configs[theme]["secondary"] + "40"};
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {theme_configs[theme]["secondary"] + "80"};
        }}
        
        /* Alerts and notifications */
        .alert-box {{
            background-color: {theme_configs[theme]["card"]};
            border-left: 4px solid {theme_configs[theme]["accent"]};
            border-radius: 6px;
            padding: 1rem;
            margin: 1rem 0;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}
        
        /* Footer */
        .footer {{
            color: {theme_configs[theme]["muted"]};
            border-top: 1px solid {theme_configs[theme]["border"]};
            padding-top: 1rem;
            margin-top: 2rem;
        }}
        
        /* Version info */
        .version-info {{
            color: {theme_configs[theme]["muted"]};
            font-size: 0.875rem;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    # Update visualization themes based on selected theme
    if theme == "Dark":
        import plotly.io as pio
        pio.templates.default = "plotly_dark"
        plt.style.use("dark_background")
        sns.set_style("darkgrid")
        sns.set_palette("husl")
    else:
        import plotly.io as pio
        pio.templates.default = "plotly"
        plt.style.use("default")
        sns.set_style("whitegrid")
        sns.set_palette("husl")

    # Add dashboard preferences
    st.sidebar.markdown("### Dashboard Preferences")
    auto_refresh = st.sidebar.checkbox("Enable Auto-refresh", value=False)
    if auto_refresh:
        refresh_interval = st.sidebar.slider("Refresh Interval (minutes)", 1, 60, 5)
        st.sidebar.info(f"Dashboard will refresh every {refresh_interval} minutes")

    # Footer with timestamp
    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    with col2:
        st.markdown("<div style='text-align: right; font-size: 0.8em; color: #666;'>Made by Zylon Labs</div>", unsafe_allow_html=True)

    # Add notification center in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("📢 Notification Center")
    
    alerts = check_alerts(df_filtered)
    if alerts:
        for alert in alerts:
            alert_style = {
                'critical': {
                    'bg': theme_configs[theme]['error'] + '22',
                    'border': theme_configs[theme]['error'],
                    'icon': '⚠️'
                },
                'warning': {
                    'bg': theme_configs[theme]['warning'] + '22',
                    'border': theme_configs[theme]['warning'],
                    'icon': '📊'
                },
                'info': {
                    'bg': theme_configs[theme]['accent'] + '22',
                    'border': theme_configs[theme]['accent'],
                    'icon': 'ℹ️'
                }
            }
            
            st.sidebar.markdown(
                f"""
                <div style='
                    background-color: {alert_style[alert['level']]['bg']};
                    border-left: 4px solid {alert_style[alert['level']]['border']};
                    border-radius: 4px;
                    padding: 12px;
                    margin: 8px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                '>
                    <div style='
                        display: flex;
                        align-items: center;
                        margin-bottom: 4px;
                        color: {theme_configs[theme]['text']};
                    '>
                        <span style='
                            font-size: 16px;
                            margin-right: 8px;
                        '>{alert_style[alert['level']]['icon']}</span>
                        <strong>{alert['message']}</strong>
                    </div>
                    <div style='
                        color: {theme_configs[theme]['text'] + "cc"};
                        font-size: 0.9em;
                        margin-left: 28px;
                    '>{alert['details']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.sidebar.markdown(
            f"""
            <div style='
                background-color: {theme_configs[theme]['success'] + '22'};
                border-left: 4px solid {theme_configs[theme]['success']};
                border-radius: 4px;
                padding: 12px;
                margin: 8px 0;
                color: {theme_configs[theme]['text']};
                display: flex;
                align-items: center;
            '>
                <span style='font-size: 16px; margin-right: 8px;'>✅</span>
                <span>All systems operating within normal parameters</span>
            </div>
            """,
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    create_dashboard() 
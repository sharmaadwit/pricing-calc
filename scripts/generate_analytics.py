#!/usr/bin/env python3
"""
Generate Advanced Analytics Reports from analytics.csv
This script creates comprehensive analytics and saves them as HTML for embedding in Flask.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
from datetime import datetime
import os

warnings.filterwarnings('ignore')

# Set style for better looking plots
plt.style.use('default')
sns.set_palette("husl")

def load_data():
    """Load and prepare the analytics data"""
    df = pd.read_csv('../analytics.csv', parse_dates=['timestamp'])
    print(f"Loaded {len(df)} records from analytics.csv")
    return df

def generate_temporal_analytics(df):
    """Generate temporal analytics plots"""
    fig, axes = plt.subplots(3, 1, figsize=(12, 12))
    
    # Hourly distribution
    df['hour'] = df['timestamp'].dt.hour
    sns.countplot(x='hour', data=df, ax=axes[0])
    axes[0].set_title('Peak Usage Hours', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Hour of Day')
    axes[0].set_ylabel('Number of Calculations')
    
    # Daily pattern
    df['weekday'] = df['timestamp'].dt.day_name()
    sns.countplot(x='weekday', data=df, order=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'], ax=axes[1])
    axes[1].set_title('Usage by Day of Week', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Day of Week')
    axes[1].set_ylabel('Number of Calculations')
    
    # Monthly trends
    df['month'] = df['timestamp'].dt.month_name()
    month_order = pd.date_range('2025-01-01', periods=12, freq='M').strftime('%B')
    sns.countplot(x='month', data=df, order=month_order, ax=axes[2])
    axes[2].set_title('Monthly Usage Trends', fontsize=14, fontweight='bold')
    axes[2].set_xlabel('Month')
    axes[2].set_ylabel('Number of Calculations')
    
    plt.tight_layout()
    return fig

def generate_customer_analytics(df):
    """Generate customer behavior analytics"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # CLV: Total platform_fee per user
    clv = df.groupby('user_name')['platform_fee'].sum().sort_values(ascending=False)
    clv.head(10).plot(kind='bar', ax=axes[0,0], title='Top 10 Customer Lifetime Value')
    axes[0,0].set_ylabel('Total Platform Fee')
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # Service Preferences
    service_cols = ['ai_price','advanced_price','basic_marketing_price','basic_utility_price']
    service_usage = df[service_cols].sum().sort_values(ascending=False)
    service_usage.plot(kind='bar', ax=axes[0,1], title='Service Preferences (Total Price)')
    axes[0,1].set_ylabel('Total Price')
    axes[0,1].tick_params(axis='x', rotation=45)
    
    # User activity over time
    user_activity = df.groupby('user_name').size().sort_values(ascending=False)
    user_activity.head(10).plot(kind='bar', ax=axes[1,0], title='Most Active Users')
    axes[1,0].set_ylabel('Number of Calculations')
    axes[1,0].tick_params(axis='x', rotation=45)
    
    # Platform fee distribution
    sns.histplot(df['platform_fee'], bins=20, kde=True, ax=axes[1,1])
    axes[1,1].set_title('Platform Fee Distribution')
    axes[1,1].set_xlabel('Platform Fee')
    axes[1,1].set_ylabel('Frequency')
    
    plt.tight_layout()
    return fig

def generate_pricing_analytics(df):
    """Generate pricing strategy analytics"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Discount Analysis
    df['ai_discount'] = (df['ai_rate_card_price'] - df['ai_price']) / df['ai_rate_card_price'].replace(0, np.nan)
    sns.histplot(df['ai_discount'].dropna(), bins=20, kde=True, ax=axes[0,0])
    axes[0,0].set_title('AI Price Discount Distribution')
    axes[0,0].set_xlabel('Discount (%)')
    
    # Price/Revenue Trends
    weekly_revenue = df.set_index('timestamp')['platform_fee'].resample('W').sum()
    weekly_revenue.plot(ax=axes[0,1], title='Weekly Platform Fee Revenue')
    axes[0,1].set_ylabel('Platform Fee Revenue')
    
    # Price comparison
    price_cols = ['ai_price', 'advanced_price', 'basic_marketing_price', 'basic_utility_price']
    price_stats = df[price_cols].describe()
    price_stats.loc['mean'].plot(kind='bar', ax=axes[1,0], title='Average Prices by Service Type')
    axes[1,0].set_ylabel('Average Price')
    axes[1,0].tick_params(axis='x', rotation=45)
    
    # Rate card vs actual
    rate_card_cols = ['ai_rate_card_price', 'advanced_rate_card_price', 'basic_marketing_rate_card_price', 'basic_utility_rate_card_price']
    actual_cols = ['ai_price', 'advanced_price', 'basic_marketing_price', 'basic_utility_price']
    
    rate_card_avg = df[rate_card_cols].mean()
    actual_avg = df[actual_cols].mean()
    
    comparison_df = pd.DataFrame({
        'Rate Card': rate_card_avg,
        'Actual': actual_avg
    })
    comparison_df.plot(kind='bar', ax=axes[1,1], title='Rate Card vs Actual Prices')
    axes[1,1].set_ylabel('Price')
    axes[1,1].tick_params(axis='x', rotation=45)
    axes[1,1].legend()
    
    plt.tight_layout()
    return fig

def generate_geographic_analytics(df):
    """Generate geographic intelligence"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Revenue by country
    country_revenue = df.groupby('country')['platform_fee'].sum().sort_values(ascending=False)
    country_revenue.plot(kind='bar', ax=axes[0,0], title='Platform Fee Revenue by Country')
    axes[0,0].set_ylabel('Total Platform Fee')
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # Currency impact
    currency_revenue = df.groupby('currency')['platform_fee'].sum().sort_values(ascending=False)
    currency_revenue.plot(kind='bar', ax=axes[0,1], title='Revenue by Currency')
    axes[0,1].set_ylabel('Total Platform Fee')
    
    # Calculations by country
    country_counts = df['country'].value_counts()
    country_counts.plot(kind='pie', autopct='%1.1f%%', ax=axes[1,0], title='Calculations by Country')
    axes[1,0].set_ylabel('')
    
    # Average platform fee by country
    avg_fee_by_country = df.groupby('country')['platform_fee'].mean().sort_values(ascending=False)
    avg_fee_by_country.plot(kind='bar', ax=axes[1,1], title='Average Platform Fee by Country')
    axes[1,1].set_ylabel('Average Platform Fee')
    axes[1,1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    return fig

def generate_resource_analytics(df):
    """Generate resource utilization analytics"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Manday efficiency
    df['total_mandays'] = df['bot_ui_mandays'].fillna(0) + df['custom_ai_mandays'].fillna(0)
    efficiency = df.groupby('user_name').apply(lambda x: x['platform_fee'].sum() / (x['total_mandays'].sum() or 1))
    efficiency.sort_values(ascending=False).head(10).plot(kind='bar', ax=axes[0,0], title='Top 10 Manday Efficiency')
    axes[0,0].set_ylabel('Platform Fee per Manday')
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # Rate variations
    rate_data = df[['bot_ui_manday_rate','custom_ai_manday_rate']].dropna()
    if not rate_data.empty:
        sns.boxplot(data=rate_data, ax=axes[0,1])
        axes[0,1].set_title('Manday Rate Variations')
        axes[0,1].set_ylabel('Rate')
    
    # Manday distribution
    manday_data = df[['bot_ui_mandays','custom_ai_mandays']].fillna(0)
    manday_data.plot(kind='box', ax=axes[1,0], title='Manday Distribution')
    axes[1,0].set_ylabel('Mandays')
    
    # Platform fee vs mandays correlation
    sns.scatterplot(x='total_mandays', y='platform_fee', data=df, ax=axes[1,1])
    axes[1,1].set_title('Platform Fee vs Total Mandays')
    axes[1,1].set_xlabel('Total Mandays')
    axes[1,1].set_ylabel('Platform Fee')
    
    plt.tight_layout()
    return fig

def generate_platform_analytics(df):
    """Generate platform/channel analytics"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Revenue by calculation route
    route_revenue = df.groupby('calculation_route')['platform_fee'].sum().sort_values(ascending=False)
    route_revenue.plot(kind='bar', ax=axes[0,0], title='Platform Fee Revenue by Calculation Route')
    axes[0,0].set_ylabel('Total Platform Fee')
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # Feature usage
    route_count = df['calculation_route'].value_counts()
    route_count.plot(kind='pie', autopct='%1.1f%%', ax=axes[0,1], title='Feature Usage by Calculation Route')
    axes[0,1].set_ylabel('')
    
    # Calculations over time by route
    route_time = df.groupby([df['timestamp'].dt.date, 'calculation_route']).size().unstack(fill_value=0)
    route_time.plot(kind='line', ax=axes[1,0], title='Calculations Over Time by Route')
    axes[1,0].set_ylabel('Number of Calculations')
    axes[1,0].set_xlabel('Date')
    axes[1,0].legend()
    
    # Average platform fee by route
    avg_fee_by_route = df.groupby('calculation_route')['platform_fee'].mean().sort_values(ascending=False)
    avg_fee_by_route.plot(kind='bar', ax=axes[1,1], title='Average Platform Fee by Route')
    axes[1,1].set_ylabel('Average Platform Fee')
    axes[1,1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    return fig

def generate_advanced_analytics(df):
    """Generate advanced statistical analytics"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Correlation matrix
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 1:
        correlation_matrix = df[numeric_cols].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', ax=axes[0,0])
        axes[0,0].set_title('Correlation Matrix')
    
    # Cohort analysis
    df['first_month'] = df.groupby('user_name')['timestamp'].transform('min').dt.to_period('M')
    cohort_counts = df.groupby('first_month')['user_name'].nunique()
    cohort_counts.plot(kind='bar', ax=axes[0,1], title='New Users by Cohort Month')
    axes[0,1].set_ylabel('Number of New Users')
    axes[0,1].tick_params(axis='x', rotation=45)
    
    # Anomaly detection
    df['platform_fee_z'] = (df['platform_fee'] - df['platform_fee'].mean()) / df['platform_fee'].std()
    anomalies = df[df['platform_fee_z'].abs() > 2]
    if not anomalies.empty:
        sns.scatterplot(x='platform_fee', y='platform_fee_z', data=df, ax=axes[1,0])
        sns.scatterplot(x='platform_fee', y='platform_fee_z', data=anomalies, color='red', ax=axes[1,0])
        axes[1,0].axhline(y=2, color='red', linestyle='--', alpha=0.5)
        axes[1,0].axhline(y=-2, color='red', linestyle='--', alpha=0.5)
        axes[1,0].set_title('Anomaly Detection (Z-score > 2)')
        axes[1,0].set_xlabel('Platform Fee')
        axes[1,0].set_ylabel('Z-score')
    
    # Volume vs revenue
    sns.scatterplot(x='ai_volume', y='platform_fee', data=df, ax=axes[1,1])
    axes[1,1].set_title('AI Volume vs Platform Fee')
    axes[1,1].set_xlabel('AI Volume')
    axes[1,1].set_ylabel('Platform Fee')
    
    plt.tight_layout()
    return fig

def generate_operational_analytics(df):
    """Generate operational analytics"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Service mix by volume
    volume_cols = ['ai_volume', 'advanced_volume', 'basic_marketing_volume', 'basic_utility_volume']
    service_mix = df[volume_cols].sum()
    service_mix.plot(kind='pie', autopct='%1.1f%%', ax=axes[0,0], title='Service Mix by Volume')
    axes[0,0].set_ylabel('')
    
    # Platform fee trends
    df.set_index('timestamp')['platform_fee'].resample('D').mean().plot(ax=axes[0,1], title='Daily Average Platform Fee')
    axes[0,1].set_ylabel('Average Platform Fee')
    
    # User engagement
    user_engagement = df.groupby('user_name').agg({
        'id': 'count',
        'platform_fee': 'sum',
        'timestamp': lambda x: (x.max() - x.min()).days
    }).rename(columns={'id': 'calculations', 'platform_fee': 'total_revenue', 'timestamp': 'days_active'})
    
    user_engagement['revenue_per_calculation'] = user_engagement['total_revenue'] / user_engagement['calculations']
    user_engagement['revenue_per_calculation'].plot(kind='hist', bins=20, ax=axes[1,0], title='Revenue per Calculation Distribution')
    axes[1,0].set_xlabel('Revenue per Calculation')
    axes[1,0].set_ylabel('Frequency')
    
    # Committed amount analysis
    if 'committed_amount' in df.columns:
        committed_data = df[df['committed_amount'].notna() & (df['committed_amount'] > 0)]
        if not committed_data.empty:
            committed_data['committed_amount'].plot(kind='hist', bins=20, ax=axes[1,1], title='Committed Amount Distribution')
            axes[1,1].set_xlabel('Committed Amount')
            axes[1,1].set_ylabel('Frequency')
    
    plt.tight_layout()
    return fig

def create_html_report():
    """Create the complete HTML report"""
    df = load_data()
    
    # Generate all analytics
    figs = []
    titles = [
        "Temporal Analytics",
        "Customer Behavior Analytics", 
        "Pricing Strategy Analytics",
        "Geographic Intelligence",
        "Resource Utilization",
        "Platform/Channel Analytics",
        "Advanced Analytics",
        "Operational Analytics"
    ]
    
    fig_funcs = [
        generate_temporal_analytics,
        generate_customer_analytics,
        generate_pricing_analytics,
        generate_geographic_analytics,
        generate_resource_analytics,
        generate_platform_analytics,
        generate_advanced_analytics,
        generate_operational_analytics
    ]
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Advanced Analytics Reports (v2)</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
            h2 { color: #34495e; margin-top: 30px; padding: 10px; background-color: #ecf0f1; border-left: 4px solid #3498db; }
            .summary { background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .metric { display: inline-block; margin: 10px; padding: 10px; background-color: #3498db; color: white; border-radius: 5px; }
            .metric-value { font-size: 24px; font-weight: bold; }
            .metric-label { font-size: 12px; }
            img { max-width: 100%; height: auto; margin: 20px 0; border: 1px solid #ddd; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Advanced Analytics Reports (v2)</h1>
            <p><em>Generated on: {}</em></p>
            
            <div class="summary">
                <h3>Executive Summary</h3>
                <div class="metric">
                    <div class="metric-value">{}</div>
                    <div class="metric-label">Total Calculations</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{}</div>
                    <div class="metric-label">Unique Users</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${:,.0f}</div>
                    <div class="metric-label">Total Revenue</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{}</div>
                    <div class="metric-label">Countries</div>
                </div>
            </div>
    """.format(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        len(df),
        df['user_name'].nunique(),
        df['platform_fee'].sum(),
        df['country'].nunique()
    )
    
    # Generate each section
    for i, (title, func) in enumerate(zip(titles, fig_funcs)):
        try:
            fig = func(df)
            # Save figure as image
            img_path = f'../static/analytics_section_{i+1}.png'
            fig.savefig(img_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            html_content += f"""
            <h2>{title}</h2>
            <img src="analytics_section_{i+1}.png" alt="{title}">
            """
        except Exception as e:
            html_content += f"""
            <h2>{title}</h2>
            <p><em>Error generating {title}: {str(e)}</em></p>
            """
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # Save HTML file
    with open('../static/analytics_reports.html', 'w') as f:
        f.write(html_content)
    
    print("Analytics report generated successfully!")
    print("Files created:")
    print("- static/analytics_reports.html (main report)")
    for i in range(len(titles)):
        print(f"- static/analytics_section_{i+1}.png (section {i+1} image)")

if __name__ == "__main__":
    create_html_report() 
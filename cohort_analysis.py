#!/usr/bin/env python3
"""
Comprehensive Cohort Analysis for Pricing Calculator Analytics

This script performs detailed cohort analysis on user behavior patterns,
retention rates, customer lifetime value, and engagement metrics.

Key Analyses:
1. User Acquisition Cohorts (by month)
2. Retention Analysis (monthly retention rates)
3. Customer Lifetime Value (CLV) by cohort
4. Revenue Cohorts (by first purchase amount)
5. Geographic Cohorts (by country/region)
6. Product Usage Cohorts (by calculation route)
7. Engagement Cohorts (by activity frequency)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from operator import attrgetter
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
try:
    plt.style.use('seaborn-v0_8')
except:
    plt.style.use('seaborn')
sns.set_palette("husl")

def load_and_prepare_data(csv_path='analytics.csv'):
    """Load and prepare analytics data for cohort analysis"""
    print("Loading analytics data...")
    df = pd.read_csv(csv_path)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', errors='coerce')
    
    # Data cleaning and preparation
    df = df.dropna(subset=['user_name', 'timestamp'])
    df = df[df['user_name'] != '']  # Remove empty user names
    
    # Add derived columns for analysis
    df['year_month'] = df['timestamp'].dt.to_period('M')
    df['year'] = df['timestamp'].dt.year
    df['month'] = df['timestamp'].dt.month
    df['week'] = df['timestamp'].dt.isocalendar().week
    df['day_of_week'] = df['timestamp'].dt.day_name()
    
    # Calculate total revenue per calculation
    df['total_revenue'] = df['platform_fee']
    
    # Calculate total volume per calculation
    df['total_volume'] = (df['ai_volume'].fillna(0) + 
                         df['advanced_volume'].fillna(0) + 
                         df['basic_marketing_volume'].fillna(0) + 
                         df['basic_utility_volume'].fillna(0))
    
    print(f"Loaded {len(df)} records for {df['user_name'].nunique()} unique users")
    return df

def analyze_user_acquisition_cohorts(df):
    """Analyze user acquisition patterns by month"""
    print("\n=== USER ACQUISITION COHORT ANALYSIS ===")
    
    # First activity per user
    first_activity = df.groupby('user_name')['timestamp'].min().reset_index()
    first_activity['acquisition_month'] = first_activity['timestamp'].dt.to_period('M')
    
    # Count new users by month
    acquisition_cohorts = first_activity.groupby('acquisition_month').size().reset_index()
    acquisition_cohorts.columns = ['Month', 'New_Users']
    
    print("New User Acquisition by Month:")
    print(acquisition_cohorts.to_string(index=False))
    
    # Visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Acquisition trend
    acquisition_cohorts.plot(x='Month', y='New_Users', kind='bar', ax=ax1, color='skyblue')
    ax1.set_title('New User Acquisition by Month')
    ax1.set_ylabel('Number of New Users')
    ax1.tick_params(axis='x', rotation=45)
    
    # Cumulative acquisition
    acquisition_cohorts['Cumulative_Users'] = acquisition_cohorts['New_Users'].cumsum()
    acquisition_cohorts.plot(x='Month', y='Cumulative_Users', kind='line', ax=ax2, marker='o', color='green')
    ax2.set_title('Cumulative User Acquisition')
    ax2.set_ylabel('Cumulative Users')
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('static/acquisition_cohorts.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return acquisition_cohorts

def analyze_retention_cohorts(df):
    """Analyze user retention by cohort"""
    print("\n=== USER RETENTION COHORT ANALYSIS ===")
    
    # Create cohort analysis
    df['first_month'] = df.groupby('user_name')['timestamp'].transform('min').dt.to_period('M')
    df['period_number'] = (df['timestamp'].dt.to_period('M') - df['first_month']).apply(attrgetter('n'))
    
    # Create cohort table
    cohort_table = df.groupby(['first_month', 'period_number'])['user_name'].nunique().reset_index()
    cohort_pivot = cohort_table.pivot(index='first_month', columns='period_number', values='user_name')
    
    # Calculate retention rates
    cohort_sizes = cohort_pivot.iloc[:, 0]
    retention_table = cohort_pivot.divide(cohort_sizes, axis=0)
    
    print("Retention Rate Matrix (rows=cohort, cols=periods since first activity):")
    print(retention_table.round(3))
    
    # Visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Retention heatmap
    sns.heatmap(retention_table, annot=True, fmt='.2f', cmap='YlOrRd', ax=ax1)
    ax1.set_title('User Retention Rate by Cohort')
    ax1.set_xlabel('Periods Since First Activity')
    ax1.set_ylabel('Acquisition Cohort')
    
    # Average retention curve
    avg_retention = retention_table.mean()
    avg_retention.plot(kind='line', marker='o', ax=ax2, color='purple')
    ax2.set_title('Average Retention Rate Over Time')
    ax2.set_xlabel('Periods Since First Activity')
    ax2.set_ylabel('Average Retention Rate')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('static/retention_cohorts.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return retention_table

def analyze_revenue_cohorts(df):
    """Analyze revenue patterns by cohort"""
    print("\n=== REVENUE COHORT ANALYSIS ===")
    
    # User-level revenue analysis
    user_revenue = df.groupby('user_name').agg({
        'total_revenue': ['sum', 'mean', 'count'],
        'timestamp': ['min', 'max'],
        'country': 'first',
        'calculation_route': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'unknown'
    }).round(2)
    
    user_revenue.columns = ['total_revenue', 'avg_revenue_per_calc', 'num_calculations', 
                           'first_activity', 'last_activity', 'country', 'preferred_route']
    
    # Calculate customer lifetime value metrics
    user_revenue['customer_lifetime_days'] = (user_revenue['last_activity'] - user_revenue['first_activity']).dt.days
    user_revenue['revenue_per_day'] = user_revenue['total_revenue'] / (user_revenue['customer_lifetime_days'] + 1)
    
    # Revenue segmentation
    revenue_segments = pd.cut(user_revenue['total_revenue'], 
                            bins=[0, 1000, 5000, 10000, float('inf')], 
                            labels=['Low Value', 'Medium Value', 'High Value', 'Premium'])
    user_revenue['revenue_segment'] = revenue_segments
    
    print("Revenue Segment Distribution:")
    print(user_revenue['revenue_segment'].value_counts())
    
    print("\nTop 10 Customers by Revenue:")
    print(user_revenue.nlargest(10, 'total_revenue')[['total_revenue', 'num_calculations', 'country', 'revenue_segment']])
    
    # Visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Revenue distribution
    user_revenue['total_revenue'].hist(bins=20, ax=ax1, color='lightblue', edgecolor='black')
    ax1.set_title('Distribution of Customer Lifetime Value')
    ax1.set_xlabel('Total Revenue per Customer')
    ax1.set_ylabel('Number of Customers')
    
    # Revenue by segment
    user_revenue['revenue_segment'].value_counts().plot(kind='bar', ax=ax2, color='lightgreen')
    ax2.set_title('Customer Distribution by Revenue Segment')
    ax2.set_ylabel('Number of Customers')
    ax2.tick_params(axis='x', rotation=45)
    
    # Revenue vs Activity
    sns.scatterplot(data=user_revenue, x='num_calculations', y='total_revenue', 
                   hue='revenue_segment', ax=ax3, s=60)
    ax3.set_title('Revenue vs Activity Level')
    ax3.set_xlabel('Number of Calculations')
    ax3.set_ylabel('Total Revenue')
    
    # Revenue by country
    country_revenue = user_revenue.groupby('country')['total_revenue'].sum().sort_values(ascending=False)
    country_revenue.plot(kind='bar', ax=ax4, color='orange')
    ax4.set_title('Total Revenue by Country')
    ax4.set_ylabel('Total Revenue')
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('static/revenue_cohorts.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return user_revenue

def analyze_geographic_cohorts(df):
    """Analyze user behavior by geographic location"""
    print("\n=== GEOGRAPHIC COHORT ANALYSIS ===")
    
    # Country-level analysis
    country_stats = df.groupby('country').agg({
        'user_name': 'nunique',
        'total_revenue': ['sum', 'mean'],
        'total_volume': ['sum', 'mean'],
        'platform_fee': ['mean', 'std'],
        'calculation_route': lambda x: x.value_counts().index[0]
    }).round(2)
    
    country_stats.columns = ['unique_users', 'total_revenue', 'avg_revenue_per_calc',
                            'total_volume', 'avg_volume_per_calc', 'avg_platform_fee', 
                            'platform_fee_std', 'most_common_route']
    
    print("Country-Level Statistics:")
    print(country_stats.sort_values('total_revenue', ascending=False))
    
    # Region analysis (if available)
    if 'region' in df.columns and df['region'].notna().any():
        region_stats = df.groupby('region').agg({
            'user_name': 'nunique',
            'total_revenue': ['sum', 'mean'],
            'total_volume': ['sum', 'mean']
        }).round(2)
        
        print("\nRegion-Level Statistics:")
        print(region_stats.sort_values(('total_revenue', 'sum'), ascending=False))
    
    # Visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Users by country
    country_stats['unique_users'].plot(kind='bar', ax=ax1, color='lightcoral')
    ax1.set_title('Number of Users by Country')
    ax1.set_ylabel('Number of Users')
    ax1.tick_params(axis='x', rotation=45)
    
    # Revenue by country
    country_stats['total_revenue'].plot(kind='bar', ax=ax2, color='lightblue')
    ax2.set_title('Total Revenue by Country')
    ax2.set_ylabel('Total Revenue')
    ax2.tick_params(axis='x', rotation=45)
    
    # Average revenue per calculation by country
    country_stats['avg_revenue_per_calc'].plot(kind='bar', ax=ax3, color='lightgreen')
    ax3.set_title('Average Revenue per Calculation by Country')
    ax3.set_ylabel('Average Revenue')
    ax3.tick_params(axis='x', rotation=45)
    
    # Volume vs Revenue scatter by country
    sns.scatterplot(data=country_stats, x='total_volume', y='total_revenue', 
                   size='unique_users', sizes=(50, 200), ax=ax4)
    ax4.set_title('Volume vs Revenue by Country')
    ax4.set_xlabel('Total Volume')
    ax4.set_ylabel('Total Revenue')
    
    plt.tight_layout()
    plt.savefig('static/geographic_cohorts.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return country_stats

def analyze_product_usage_cohorts(df):
    """Analyze product usage patterns by calculation route"""
    print("\n=== PRODUCT USAGE COHORT ANALYSIS ===")
    
    # Route-based analysis
    route_stats = df.groupby('calculation_route').agg({
        'user_name': 'nunique',
        'total_revenue': ['sum', 'mean'],
        'total_volume': ['sum', 'mean'],
        'platform_fee': ['mean', 'std'],
        'committed_amount': ['mean', 'std']
    }).round(2)
    
    print("Calculation Route Statistics:")
    print(route_stats)
    
    # User behavior by route preference
    user_route_preference = df.groupby('user_name')['calculation_route'].apply(
        lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'mixed'
    ).reset_index()
    user_route_preference.columns = ['user_name', 'preferred_route']
    
    # Merge with user revenue data
    user_revenue = df.groupby('user_name')['total_revenue'].sum().reset_index()
    user_route_analysis = user_route_preference.merge(user_revenue, on='user_name')
    
    print("\nUser Behavior by Route Preference:")
    route_preference_stats = user_route_analysis.groupby('preferred_route').agg({
        'user_name': 'count',
        'total_revenue': ['sum', 'mean']
    }).round(2)
    print(route_preference_stats)
    
    # Visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Usage distribution
    df['calculation_route'].value_counts().plot(kind='pie', ax=ax1, autopct='%1.1f%%')
    ax1.set_title('Distribution of Calculation Routes')
    
    # Revenue by route
    route_stats[('total_revenue', 'sum')].plot(kind='bar', ax=ax2, color='lightblue')
    ax2.set_title('Total Revenue by Calculation Route')
    ax2.set_ylabel('Total Revenue')
    ax2.tick_params(axis='x', rotation=45)
    
    # Average revenue per calculation by route
    route_stats[('total_revenue', 'mean')].plot(kind='bar', ax=ax3, color='lightgreen')
    ax3.set_title('Average Revenue per Calculation by Route')
    ax3.set_ylabel('Average Revenue')
    ax3.tick_params(axis='x', rotation=45)
    
    # Volume vs Revenue by route
    sns.scatterplot(data=df, x='total_volume', y='total_revenue', 
                   hue='calculation_route', ax=ax4, s=60)
    ax4.set_title('Volume vs Revenue by Calculation Route')
    ax4.set_xlabel('Total Volume')
    ax4.set_ylabel('Total Revenue')
    
    plt.tight_layout()
    plt.savefig('static/product_usage_cohorts.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return route_stats, user_route_analysis

def analyze_engagement_cohorts(df):
    """Analyze user engagement patterns"""
    print("\n=== ENGAGEMENT COHORT ANALYSIS ===")
    
    # Calculate engagement metrics per user
    user_engagement = df.groupby('user_name').agg({
        'timestamp': ['min', 'max', 'count'],
        'total_revenue': 'sum',
        'total_volume': 'sum',
        'country': 'first'
    })
    
    user_engagement.columns = ['first_activity', 'last_activity', 'num_calculations', 
                             'total_revenue', 'total_volume', 'country']
    
    # Calculate engagement metrics
    user_engagement['days_active'] = (user_engagement['last_activity'] - user_engagement['first_activity']).dt.days
    user_engagement['calculations_per_day'] = user_engagement['num_calculations'] / (user_engagement['days_active'] + 1)
    user_engagement['avg_days_between_calculations'] = user_engagement['days_active'] / (user_engagement['num_calculations'] - 1)
    
    # Engagement segmentation
    engagement_segments = pd.cut(user_engagement['num_calculations'], 
                               bins=[0, 1, 5, 10, float('inf')], 
                               labels=['Low Engagement', 'Medium Engagement', 'High Engagement', 'Very High Engagement'])
    user_engagement['engagement_segment'] = engagement_segments
    
    print("Engagement Segment Distribution:")
    print(user_engagement['engagement_segment'].value_counts())
    
    print("\nTop 10 Most Engaged Users:")
    print(user_engagement.nlargest(10, 'num_calculations')[['num_calculations', 'days_active', 'calculations_per_day', 'total_revenue']])
    
    # Activity patterns over time
    daily_activity = df.groupby(df['timestamp'].dt.date)['user_name'].nunique().reset_index()
    daily_activity.columns = ['date', 'active_users']
    
    # Visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Engagement distribution
    user_engagement['num_calculations'].hist(bins=20, ax=ax1, color='lightcoral', edgecolor='black')
    ax1.set_title('Distribution of User Engagement (Calculations per User)')
    ax1.set_xlabel('Number of Calculations')
    ax1.set_ylabel('Number of Users')
    
    # Engagement segments
    user_engagement['engagement_segment'].value_counts().plot(kind='bar', ax=ax2, color='lightblue')
    ax2.set_title('User Distribution by Engagement Level')
    ax2.set_ylabel('Number of Users')
    ax2.tick_params(axis='x', rotation=45)
    
    # Activity over time
    daily_activity.plot(x='date', y='active_users', kind='line', ax=ax3, color='green')
    ax3.set_title('Daily Active Users Over Time')
    ax3.set_ylabel('Number of Active Users')
    ax3.tick_params(axis='x', rotation=45)
    
    # Engagement vs Revenue
    sns.scatterplot(data=user_engagement, x='num_calculations', y='total_revenue', 
                   hue='engagement_segment', ax=ax4, s=60)
    ax4.set_title('Engagement vs Revenue')
    ax4.set_xlabel('Number of Calculations')
    ax4.set_ylabel('Total Revenue')
    
    plt.tight_layout()
    plt.savefig('static/engagement_cohorts.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return user_engagement

def generate_cohort_summary_report(df, acquisition_cohorts, retention_table, user_revenue, 
                                 country_stats, route_stats, user_engagement):
    """Generate a comprehensive cohort analysis summary report"""
    print("\n" + "="*60)
    print("COMPREHENSIVE COHORT ANALYSIS SUMMARY REPORT")
    print("="*60)
    
    # Overall metrics
    total_users = df['user_name'].nunique()
    total_calculations = len(df)
    total_revenue = df['total_revenue'].sum()
    avg_revenue_per_user = total_revenue / total_users
    avg_calculations_per_user = total_calculations / total_users
    
    print(f"\nOVERALL METRICS:")
    print(f"Total Users: {total_users:,}")
    print(f"Total Calculations: {total_calculations:,}")
    print(f"Total Revenue: ${total_revenue:,.2f}")
    print(f"Average Revenue per User: ${avg_revenue_per_user:,.2f}")
    print(f"Average Calculations per User: {avg_calculations_per_user:.1f}")
    
    # Top performing cohorts
    print(f"\nTOP PERFORMING COHORTS:")
    print(f"Highest Revenue Country: {country_stats['total_revenue'].idxmax()} (${country_stats['total_revenue'].max():,.2f})")
    print(f"Most Active Country: {country_stats['unique_users'].idxmax()} ({country_stats['unique_users'].max()} users)")
    print(f"Most Popular Route: {route_stats[('total_revenue', 'sum')].idxmax()} (${route_stats[('total_revenue', 'sum')].max():,.2f})")
    
    # User segmentation insights
    print(f"\nUSER SEGMENTATION INSIGHTS:")
    print(f"Revenue Segments: {user_revenue['revenue_segment'].value_counts().to_dict()}")
    print(f"Engagement Segments: {user_engagement['engagement_segment'].value_counts().to_dict()}")
    
    # Retention insights
    if not retention_table.empty:
        avg_retention_1_month = retention_table.iloc[:, 1].mean() if retention_table.shape[1] > 1 else 0
        avg_retention_3_month = retention_table.iloc[:, 3].mean() if retention_table.shape[1] > 3 else 0
        print(f"\nRETENTION INSIGHTS:")
        print(f"Average 1-Month Retention: {avg_retention_1_month:.1%}")
        print(f"Average 3-Month Retention: {avg_retention_3_month:.1%}")
    
    # Growth insights
    if len(acquisition_cohorts) > 1:
        recent_growth = acquisition_cohorts['New_Users'].iloc[-3:].mean()
        earlier_growth = acquisition_cohorts['New_Users'].iloc[:-3].mean() if len(acquisition_cohorts) > 3 else recent_growth
        growth_rate = ((recent_growth - earlier_growth) / earlier_growth * 100) if earlier_growth > 0 else 0
        print(f"\nGROWTH INSIGHTS:")
        print(f"Recent User Acquisition Rate: {recent_growth:.1f} users/month")
        print(f"Growth Rate: {growth_rate:+.1f}%")
    
    print("\n" + "="*60)
    print("END OF COHORT ANALYSIS REPORT")
    print("="*60)

def main():
    """Main function to run comprehensive cohort analysis"""
    print("Starting Comprehensive Cohort Analysis...")
    
    # Load and prepare data
    df = load_and_prepare_data()
    
    # Run all cohort analyses
    acquisition_cohorts = analyze_user_acquisition_cohorts(df)
    retention_table = analyze_retention_cohorts(df)
    user_revenue = analyze_revenue_cohorts(df)
    country_stats = analyze_geographic_cohorts(df)
    route_stats, user_route_analysis = analyze_product_usage_cohorts(df)
    user_engagement = analyze_engagement_cohorts(df)
    
    # Generate summary report
    generate_cohort_summary_report(df, acquisition_cohorts, retention_table, user_revenue,
                                 country_stats, route_stats, user_engagement)
    
    print("\nCohort analysis complete! Charts saved to static/ directory.")
    print("Generated files:")
    print("- static/acquisition_cohorts.png")
    print("- static/retention_cohorts.png") 
    print("- static/revenue_cohorts.png")
    print("- static/geographic_cohorts.png")
    print("- static/product_usage_cohorts.png")
    print("- static/engagement_cohorts.png")

if __name__ == "__main__":
    main()

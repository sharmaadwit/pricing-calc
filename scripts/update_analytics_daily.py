#!/usr/bin/env python3
"""
Daily Analytics Update Script
Automatically exports data from PostgreSQL, updates analytics.csv, and refreshes analyticsv2
Runs daily at 8 PM IST via cron job
"""

import os
import sys
import psycopg2
import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
from datetime import datetime, timedelta
import json
import subprocess
import math
import time
start_time = time.time()
print(f"[DEBUG] Script started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

warnings.filterwarnings('ignore')

# Configuration
DB_URL = "postgresql://postgres:prdeuXwtBzpLZaOGpxgRspfjfLNEQrys@gondola.proxy.rlwy.net:25504/railway"
CSV_PATH = "analytics.csv"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

def log_message(message):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def export_analytics_to_csv():
    """Export analytics data from PostgreSQL to CSV"""
    try:
        log_message("Starting CSV export from PostgreSQL...")
        
        # Connect to database
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        # Export all data from analytics table
        cur.execute("SELECT * FROM analytics ORDER BY timestamp DESC")
        
        if cur.description is None:
            log_message("Error: No data found in analytics table")
            return False
            
        columns = [desc[0] for desc in cur.description]
        
        # Write to CSV
        with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            for row in cur.fetchall():
                writer.writerow(row)
        
        cur.close()
        conn.close()
        
        log_message(f"Successfully exported data to {CSV_PATH}")
        return True
        
    except Exception as e:
        log_message(f"Error exporting CSV: {e}")
        return False

def generate_analytics_charts():
    """Generate analytics charts and save as images"""
    try:
        log_message("Generating analytics charts...")
        
        # Load data
        df = pd.read_csv(CSV_PATH, parse_dates=['timestamp'])
        log_message(f"Loaded {len(df)} records from {CSV_PATH}")
        
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create static directory if it doesn't exist
        static_dir = os.path.join(PROJECT_ROOT, 'static')
        os.makedirs(static_dir, exist_ok=True)
        
        # Generate charts
        charts = [
            ('temporal', generate_temporal_charts, df),
            ('customer', generate_customer_charts, df),
            ('pricing', generate_pricing_charts, df),
            ('geographic', generate_geographic_charts, df),
            ('resource', generate_resource_charts, df),
            ('platform', generate_platform_charts, df)
        ]
        
        for chart_name, chart_func, data in charts:
            try:
                chart_func(data, static_dir)
                log_message(f"Generated {chart_name} charts")
            except Exception as e:
                log_message(f"Error generating {chart_name} charts: {e}")
        
        return True
        
    except Exception as e:
        log_message(f"Error generating charts: {e}")
        return False

def generate_temporal_charts(df, static_dir):
    """Generate temporal analytics charts"""
    # Ensure timestamp is datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # Hourly distribution
    df['hour'] = df['timestamp'].dt.hour
    hourly_counts = df['hour'].value_counts().sort_index()
    bars0 = axes[0].bar(hourly_counts.index, hourly_counts.values, color='#667eea')
    axes[0].set_title('Peak Usage Hours', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Hour of Day')
    axes[0].set_ylabel('Number of Calculations')
    # Add data labels
    axes[0].bar_label(bars0, fmt=lambda x: f'{int(x)}' if x == int(x) else f'{x:.3f}')
    
    # Daily pattern
    df['weekday'] = df['timestamp'].dt.day_name()
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_counts = df['weekday'].value_counts().reindex(weekday_order)
    bars1 = axes[1].bar(range(len(weekday_counts)), weekday_counts.values, color='#764ba2')
    axes[1].set_title('Usage by Day of Week', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Day of Week')
    axes[1].set_ylabel('Number of Calculations')
    axes[1].set_xticks(range(len(weekday_counts)))
    axes[1].set_xticklabels(weekday_counts.index, rotation=45)
    # Add data labels
    axes[1].bar_label(bars1, fmt=lambda x: f'{int(x)}' if x == int(x) else f'{x:.3f}')
    
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'temporal_analytics.png'), dpi=300, bbox_inches='tight')
    plt.close()

def generate_customer_charts(df, static_dir):
    """Generate customer behavior charts"""
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # CLV
    clv = df.groupby('user_name')['platform_fee'].sum().sort_values(ascending=False).head(10)
    bars0 = axes[0].bar(range(len(clv)), clv.values, color='#f093fb')
    axes[0].set_title('Top 10 Customer Lifetime Value', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Total Platform Fee (₹)')
    axes[0].set_xticks(range(len(clv)))
    axes[0].set_xticklabels(clv.index, rotation=45)
    # Add data labels
    axes[0].bar_label(bars0, fmt=lambda x: f'{int(x)}' if x == int(x) else f'{x:.3f}')
    
    # Service preferences
    service_cols = ['ai_price', 'advanced_price', 'basic_marketing_price', 'basic_utility_price']
    service_usage = df[service_cols].sum().sort_values(ascending=False)
    bars1 = axes[1].bar(range(len(service_usage)), service_usage.values, color='#667eea')
    axes[1].set_title('Service Preferences (Total Price)', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('Total Price')
    axes[1].set_xticks(range(len(service_usage)))
    axes[1].set_xticklabels(service_usage.index, rotation=45)
    # Add data labels
    axes[1].bar_label(bars1, fmt=lambda x: f'{int(x)}' if x == int(x) else f'{x:.3f}')
    
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'customer_analytics.png'), dpi=300, bbox_inches='tight')
    plt.close()

def generate_pricing_charts(df, static_dir):
    """Generate pricing strategy charts"""
    # Ensure timestamp is datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # Weekly revenue
    weekly_revenue = df.set_index('timestamp')['platform_fee'].resample('W').sum()
    line0, = axes[0].plot(weekly_revenue.index, weekly_revenue.values, marker='o', color='#4facfe', linewidth=2)
    axes[0].set_title('Weekly Platform Fee Revenue', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Revenue (₹)')
    axes[0].tick_params(axis='x', rotation=45)
    # Add data labels to line plot
    for x, y in zip(weekly_revenue.index, weekly_revenue.values):
        axes[0].annotate(f'{int(y) if y == int(y) else f"{y:.3f}"}', xy=(x, y), xytext=(0, 5), textcoords='offset points', ha='center', fontsize=8)
    
    # Price comparison
    price_cols = ['ai_price', 'advanced_price', 'basic_marketing_price', 'basic_utility_price']
    avg_prices = df[price_cols].mean()
    bars1 = axes[1].bar(range(len(avg_prices)), avg_prices.values, color='#43e97b')
    axes[1].set_title('Average Prices by Service Type', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('Average Price')
    axes[1].set_xticks(range(len(avg_prices)))
    axes[1].set_xticklabels(avg_prices.index, rotation=45)
    # Add data labels
    axes[1].bar_label(bars1, fmt=lambda x: f'{int(x)}' if x == int(x) else f'{x:.3f}')
    
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'pricing_analytics.png'), dpi=300, bbox_inches='tight')
    plt.close()

def generate_geographic_charts(df, static_dir):
    """Generate geographic intelligence charts"""
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # Revenue by country
    country_revenue = df.groupby('country')['platform_fee'].sum().sort_values(ascending=False)
    bars0 = axes[0].bar(range(len(country_revenue)), country_revenue.values, color='#fa709a')
    axes[0].set_title('Platform Fee Revenue by Country', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Total Platform Fee (₹)')
    axes[0].set_xticks(range(len(country_revenue)))
    axes[0].set_xticklabels(country_revenue.index, rotation=45)
    # Add data labels
    axes[0].bar_label(bars0, fmt=lambda x: f'{int(x)}' if x == int(x) else f'{x:.3f}')
    
    # Calculations by country
    country_counts = df['country'].value_counts()
    axes[1].pie(country_counts.values, labels=country_counts.index, autopct='%1.1f%%', colors=['#667eea', '#764ba2'])
    axes[1].set_title('Calculations by Country', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'geographic_analytics.png'), dpi=300, bbox_inches='tight')
    plt.close()

def generate_resource_charts(df, static_dir):
    """Generate resource utilization charts"""
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # Manday efficiency
    df['total_mandays'] = df['bot_ui_mandays'].fillna(0) + df['custom_ai_mandays'].fillna(0)
    efficiency = df.groupby('user_name').apply(lambda x: x['platform_fee'].sum() / (x['total_mandays'].sum() or 1))
    efficiency = efficiency.sort_values(ascending=False).head(10)
    axes[0].bar(range(len(efficiency)), efficiency.values, color='#a8edea')
    axes[0].set_title('Top 10 Manday Efficiency', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Platform Fee per Manday (₹)')
    axes[0].set_xticks(range(len(efficiency)))
    axes[0].set_xticklabels(efficiency.index, rotation=45)
    
    # Rate variations
    rate_data = df[['bot_ui_manday_rate', 'custom_ai_manday_rate']].dropna()
    if not rate_data.empty:
        axes[1].boxplot([rate_data['bot_ui_manday_rate'], rate_data['custom_ai_manday_rate']], 
                       labels=['Bot UI', 'Custom AI'])
        axes[1].set_title('Manday Rate Variations', fontsize=14, fontweight='bold')
        axes[1].set_ylabel('Rate (₹)')
    
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'resource_analytics.png'), dpi=300, bbox_inches='tight')
    plt.close()

def generate_platform_charts(df, static_dir):
    """Generate platform analytics charts"""
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # Revenue by route
    route_revenue = df.groupby('calculation_route')['platform_fee'].sum().sort_values(ascending=False)
    bars0 = axes[0].bar(range(len(route_revenue)), route_revenue.values, color='#ffecd2')
    axes[0].set_title('Platform Fee Revenue by Calculation Route', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Total Platform Fee (₹)')
    axes[0].set_xticks(range(len(route_revenue)))
    axes[0].set_xticklabels(route_revenue.index, rotation=45)
    # Add data labels
    axes[0].bar_label(bars0, fmt=lambda x: f'{int(x)}' if x == int(x) else f'{x:.2f}')
    
    # Feature usage
    route_count = df['calculation_route'].value_counts()
    axes[1].pie(route_count.values, labels=route_count.index, autopct='%1.1f%%', colors=['#667eea', '#764ba2'])
    axes[1].set_title('Feature Usage by Calculation Route', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(static_dir, 'platform_analytics.png'), dpi=300, bbox_inches='tight')
    plt.close()

def update_analytics_summary():
    """Update analytics summary data for the dashboard"""
    try:
        log_message("Updating analytics summary...")
        
        df = pd.read_csv(CSV_PATH, parse_dates=['timestamp'])
        
        # Calculate summary statistics
        summary = {
            'total_calculations': len(df),
            'unique_users': df['user_name'].nunique(),
            'total_revenue': df['platform_fee'].sum(),
            'countries': df['country'].nunique(),
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'top_users': df.groupby('user_name')['platform_fee'].sum().sort_values(ascending=False).head(5).to_dict(),
            'country_breakdown': df['country'].value_counts().to_dict(),
            'route_breakdown': df['calculation_route'].value_counts().to_dict()
        }

        # Per-country stats
        country_stats = {}
        region_stats = {}
        # Define rate card (list) prices for each country (from pricing_config.py)
        LIST_PRICES = {
            'India': {'bot_ui': 20000, 'custom_ai': 30000},
            'LATAM': {'bot_ui': 580, 'custom_ai': 750},
            'MENA': {'bot_ui': 300, 'custom_ai': 500},
            'Africa': {'bot_ui': 300, 'custom_ai': 420},
            'Europe': {'bot_ui': 300, 'custom_ai': 420},
            'Rest of the World': {'bot_ui': 300, 'custom_ai': 420},
        }
        from pricing_config import committed_amount_slabs
        def get_list_price(country, msg_type):
            slabs = committed_amount_slabs.get(country, committed_amount_slabs.get('Rest of the World', []))
            if not slabs:
                return 0.0
            # Find the highest price for the message type across all slabs (usually the first slab, lowest committed amount)
            max_price = 0.0
            for slab in slabs:
                price = slab[2].get(msg_type, 0.0)
                if price > max_price:
                    max_price = price
            return max_price
        for country, group in df.groupby('country'):
            currency = group['currency'].dropna().iloc[0] if 'currency' in group and not group['currency'].dropna().empty else ''
            # --- Per-country arrays for charts ---
            # Weekly revenue
            group['timestamp'] = pd.to_datetime(group['timestamp'], errors='coerce')
            weekly_revenue = group.set_index('timestamp')['platform_fee'].resample('W').sum()
            weekly_revenue_labels = [d.strftime('%Y-%m-%d') for d in weekly_revenue.index]
            # CLV
            clv_series = group.groupby('user_name')['platform_fee'].sum().sort_values(ascending=False).head(10)
            clv = clv_series.values.tolist()
            clv_labels = clv_series.index.tolist()
            # Service usage
            service_cols = ['ai_price', 'advanced_price', 'basic_marketing_price', 'basic_utility_price']
            service_usage_series = group[service_cols].sum().sort_values(ascending=False)
            service_usage = service_usage_series.values.tolist()
            service_labels = service_usage_series.index.tolist()
            # Manday efficiency
            group['total_mandays'] = group['bot_ui_mandays'].fillna(0) + group['custom_ai_mandays'].fillna(0)
            manday_efficiency_series = group.groupby('user_name').apply(lambda x: x['platform_fee'].sum() / (x['total_mandays'].sum() or 1)).sort_values(ascending=False).head(10)
            manday_efficiency = manday_efficiency_series.values.tolist()
            manday_efficiency_labels = manday_efficiency_series.index.tolist()
            # Hourly counts
            group['hour'] = group['timestamp'].dt.hour
            hourly_counts_series = group['hour'].value_counts().sort_index()
            hourly_counts = hourly_counts_series.values.tolist()
            hourly_labels = [str(h) + ':00' for h in hourly_counts_series.index]
            # Weekday counts
            group['weekday'] = group['timestamp'].dt.day_name()
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_counts_series = group['weekday'].value_counts().reindex(weekday_order)
            weekday_counts = weekday_counts_series.values.tolist()
            weekday_labels = weekday_order
            # Route revenue
            route_revenue_series = group.groupby('calculation_route')['platform_fee'].sum().sort_values(ascending=False)
            route_revenue = route_revenue_series.values.tolist()
            route_labels = route_revenue_series.index.tolist()
            # Route counts
            route_counts_series = group['calculation_route'].value_counts()
            route_counts = route_counts_series.values.tolist()
            # Manday rates (list and average)
            if country == 'LATAM':
                list_bot = LIST_PRICES.get(country, {}).get('bot_ui', float(group['bot_ui_manday_rate'].dropna().mean()) if 'bot_ui_manday_rate' in group else 0)
                list_ai = LIST_PRICES.get(country, {}).get('custom_ai', float(group['custom_ai_manday_rate'].dropna().mean()) if 'custom_ai_manday_rate' in group else 0)
            else:
                list_bot = LIST_PRICES.get(country, {}).get('bot_ui', float(group['bot_ui_manday_rate'].dropna().mean()) if 'bot_ui_manday_rate' in group else 0)
                list_ai = LIST_PRICES.get(country, {}).get('custom_ai', float(group['custom_ai_manday_rate'].dropna().mean()) if 'custom_ai_manday_rate' in group else 0)
            avg_bot = float(group['bot_ui_manday_rate'].dropna().mean()) if 'bot_ui_manday_rate' in group else 0
            avg_ai = float(group['custom_ai_manday_rate'].dropna().mean()) if 'custom_ai_manday_rate' in group else 0
            bot_ui_manday_rate = {
                'list': list_bot,
                'average': avg_bot
            }
            custom_ai_manday_rate = {
                'list': list_ai,
                'average': avg_ai
            }
            # Restore stat function for summary stats
            def stat(col):
                if col not in group.columns:
                    return {'average': 0, 'min': 0, 'max': 0, 'median': 0}
                try:
                    vals = pd.to_numeric(group[col], errors='coerce').dropna()
                    if vals.empty:
                        return {'average': 0, 'min': 0, 'max': 0, 'median': 0}
                    return {
                        'average': float(vals.mean()),
                        'min': float(vals.min()),
                        'max': float(vals.max()),
                        'median': float(vals.median())
                    }
                except Exception as e:
                    print(f"Error in stat() for column '{col}' in country '{country}': {e}")
                    return {'average': 0, 'min': 0, 'max': 0, 'median': 0}
            # Restore avg_discount function for discount calculations
            def avg_discount(actual, rate_card):
                try:
                    if actual not in group.columns or rate_card not in group.columns:
                        return 0
                    vals = group[[actual, rate_card]].dropna()
                    vals = vals[pd.to_numeric(vals[rate_card], errors='coerce') != 0]
                    vals[actual] = pd.to_numeric(vals[actual], errors='coerce')
                    vals[rate_card] = pd.to_numeric(vals[rate_card], errors='coerce')
                    valid = vals.dropna()
                    if valid.empty:
                        return 0
                    return float(((valid[rate_card] - valid[actual]) / valid[rate_card]).mean() * 100)
                except Exception as e:
                    print(f"Error in avg_discount() for columns '{actual}', '{rate_card}' in country '{country}': {e}")
                    return 0
            print(f"Building stats for country: {country}")
            country_stats[country] = {
                'currency': currency,
                'platform_fee': stat('platform_fee'),
                'ai_message': dict(stat('ai_price'), list=get_list_price(country, 'ai')),
                'advanced_message': dict(stat('advanced_price'), list=get_list_price(country, 'advanced')),
                'basic_marketing_message': dict(stat('basic_marketing_price'), list=get_list_price(country, 'basic_marketing')),
                'basic_utility_message': dict(stat('basic_utility_price'), list=get_list_price(country, 'basic_utility')),
                'voice_notes_rate': stat('voice_notes_rate'),
                'committed_amount': stat('committed_amount'),
                'one_time_dev_cost': stat('bot_ui_manday_rate') if 'bot_ui_manday_rate' in group else {},
                'bot_ui_manday_cost': stat('bot_ui_manday_rate'),
                'custom_ai_manday_cost': stat('custom_ai_manday_rate'),
                'discounts': {
                    'ai_message': avg_discount('ai_price', 'ai_rate_card_price'),
                    'advanced_message': avg_discount('advanced_price', 'advanced_rate_card_price'),
                    'basic_marketing_message': avg_discount('basic_marketing_price', 'basic_marketing_rate_card_price'),
                    'basic_utility_message': avg_discount('basic_utility_price', 'basic_utility_rate_card_price'),
                    'bot_ui_manday_rate': 0,
                    'custom_ai_manday_rate': 0,
                },
                # --- Per-country arrays for charts ---
                'weekly_revenue': weekly_revenue.values.tolist(),
                'weekly_revenue_labels': weekly_revenue_labels,
                'clv': clv,
                'clv_labels': clv_labels,
                'service_usage': service_usage,
                'service_labels': service_labels,
                'manday_efficiency': manday_efficiency,
                'manday_efficiency_labels': manday_efficiency_labels,
                'hourly_counts': hourly_counts,
                'hourly_labels': hourly_labels,
                'weekday_counts': weekday_counts,
                'weekday_labels': weekday_labels,
                'route_revenue': route_revenue,
                'route_labels': route_labels,
                'route_counts': route_counts,
                'bot_ui_manday_rate': bot_ui_manday_rate,
                'custom_ai_manday_rate': custom_ai_manday_rate
            }
        # Per-country, per-region stats
        for (country, region), group in df.groupby(['country', 'region']):
            currency = group['currency'].dropna().iloc[0] if 'currency' in group and not group['currency'].dropna().empty else ''
            def stat(col):
                if col not in group.columns:
                    return {'average': 0, 'min': 0, 'max': 0, 'median': 0}
                try:
                    vals = pd.to_numeric(group[col], errors='coerce').dropna()
                    if vals.empty:
                        return {'average': 0, 'min': 0, 'max': 0, 'median': 0}
                    return {
                        'average': float(vals.mean()),
                        'min': float(vals.min()),
                        'max': float(vals.max()),
                        'median': float(vals.median())
                    }
                except Exception as e:
                    print(f"Error in stat() for column '{col}' in country '{country}', region '{region}': {e}")
                    return {'average': 0, 'min': 0, 'max': 0, 'median': 0}
            def avg_discount(actual, rate_card):
                try:
                    if actual not in group.columns or rate_card not in group.columns:
                        return 0
                    vals = group[[actual, rate_card]].dropna()
                    vals = vals[pd.to_numeric(vals[rate_card], errors='coerce') != 0]
                    vals[actual] = pd.to_numeric(vals[actual], errors='coerce')
                    vals[rate_card] = pd.to_numeric(vals[rate_card], errors='coerce')
                    valid = vals.dropna()
                    if valid.empty:
                        return 0
                    return float(((valid[rate_card] - valid[actual]) / valid[rate_card]).mean() * 100)
                except Exception as e:
                    print(f"Error in avg_discount() for columns '{actual}', '{rate_card}' in country '{country}', region '{region}': {e}")
                    return 0
            if country not in region_stats:
                region_stats[country] = {}
            region_stats[country][region] = {
                'currency': currency,
                'platform_fee': stat('platform_fee'),
                'ai_message': dict(stat('ai_price'), list=get_list_price(country, 'ai')),
                'advanced_message': dict(stat('advanced_price'), list=get_list_price(country, 'advanced')),
                'basic_marketing_message': dict(stat('basic_marketing_price'), list=get_list_price(country, 'basic_marketing')),
                'basic_utility_message': dict(stat('basic_utility_price'), list=get_list_price(country, 'basic_utility')),
                'voice_notes_rate': stat('voice_notes_rate'),
                'committed_amount': stat('committed_amount'),
                'one_time_dev_cost': stat('bot_ui_manday_rate') if 'bot_ui_manday_rate' in group else {},
                'bot_ui_manday_cost': stat('bot_ui_manday_rate'),
                'custom_ai_manday_cost': stat('custom_ai_manday_rate'),
                'discounts': {
                    'ai_message': avg_discount('ai_price', 'ai_rate_card_price'),
                    'advanced_message': avg_discount('advanced_price', 'advanced_rate_card_price'),
                    'basic_marketing_message': avg_discount('basic_marketing_price', 'basic_marketing_rate_card_price'),
                    'basic_utility_message': avg_discount('basic_utility_price', 'basic_utility_rate_card_price'),
                    'bot_ui_manday_rate': 0,
                    'custom_ai_manday_rate': 0,
                },
            }
        summary['country_stats'] = country_stats
        summary['region_stats'] = region_stats
        # Add aggregate arrays for Distribution by Country
        summary['platform_fee_by_country'] = [country_stats[c]['platform_fee']['average'] for c in country_stats]
        summary['ai_message_by_country'] = [country_stats[c]['ai_message']['average'] for c in country_stats]
        summary['country_labels'] = list(country_stats.keys())
        
        # Save summary to JSON file
        summary_path = os.path.join(PROJECT_ROOT, 'static', 'analytics_summary.json')
        summary = clean_nans(summary)
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        log_message("Analytics summary updated successfully")
        return True
        
    except Exception as e:
        log_message(f"Error updating analytics summary: {e}")
        return False

def clean_nans(obj):
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    elif isinstance(obj, dict):
        return {k: clean_nans(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nans(x) for x in obj]
    else:
        return obj

def main():
    """Main function to run the daily analytics update"""
    log_message("Starting daily analytics update process...")
    
    # Change to project root directory
    os.chdir(PROJECT_ROOT)
    
    # Step 1: Export data from PostgreSQL
    if not export_analytics_to_csv():
        log_message("Failed to export CSV. Exiting.")
        sys.exit(1)
    print(f"[DEBUG] After DB export: {time.time() - start_time:.3f} seconds elapsed")
    
    # Step 2: Generate analytics charts
    if not generate_analytics_charts():
        log_message("Failed to generate charts. Continuing...")
    print(f"[DEBUG] After chart generation: {time.time() - start_time:.3f} seconds elapsed")
    
    # Step 3: Update analytics summary
    if not update_analytics_summary():
        log_message("Failed to update summary. Continuing...")
    print(f"[DEBUG] After writing summary JSON: {time.time() - start_time:.3f} seconds elapsed")
    
    log_message("Daily analytics update completed successfully!")
    print(f"[DEBUG] Script finished at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[DEBUG] Total execution time: {time.time() - start_time:.3f} seconds")

if __name__ == "__main__":
    main() 
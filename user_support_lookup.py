#!/usr/bin/env python3
"""
User Support Lookup Tool for Pricing Calculator
Allows support staff to quickly find calculation details by ID
"""

import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Analytics
from logging_config import setup_logging, log_user_support_lookup

def lookup_calculation_by_id(calculation_id):
    """
    Look up a calculation by its ID from the database
    
    Args:
        calculation_id (str): The calculation ID to look up
        
    Returns:
        dict: Calculation details or None if not found
    """
    with app.app_context():
        try:
            # Try to find by exact calculation_id
            analytics_record = Analytics.query.filter_by(calculation_id=calculation_id).first()
            
            if analytics_record:
                # Convert to dictionary for easy access
                result = {
                    'calculation_id': analytics_record.calculation_id,
                    'timestamp': analytics_record.timestamp.strftime('%Y-%m-%d %H:%M:%S') if analytics_record.timestamp else 'N/A',
                    'user_name': analytics_record.user_name,
                    'country': analytics_record.country,
                    'region': analytics_record.region,
                    'currency': analytics_record.currency,
                    'calculation_route': analytics_record.calculation_route,
                    
                    # Input volumes
                    'ai_volume': analytics_record.ai_volume,
                    'advanced_volume': analytics_record.advanced_volume,
                    'basic_marketing_volume': analytics_record.basic_marketing_volume,
                    'basic_utility_volume': analytics_record.basic_utility_volume,
                    'committed_amount': analytics_record.committed_amount,
                    
                    # Pricing
                    'ai_price': analytics_record.ai_price,
                    'advanced_price': analytics_record.advanced_price,
                    'basic_marketing_price': analytics_record.basic_marketing_price,
                    'basic_utility_price': analytics_record.basic_utility_price,
                    'platform_fee': analytics_record.platform_fee,
                    
                    # Rate card prices
                    'ai_rate_card_price': analytics_record.ai_rate_card_price,
                    'advanced_rate_card_price': analytics_record.advanced_rate_card_price,
                    'basic_marketing_rate_card_price': analytics_record.basic_marketing_rate_card_price,
                    'basic_utility_rate_card_price': analytics_record.basic_utility_rate_card_price,
                    
                    # Manday information
                    'bot_ui_manday_rate': analytics_record.bot_ui_manday_rate,
                    'custom_ai_manday_rate': analytics_record.custom_ai_manday_rate,
                    'bot_ui_mandays': analytics_record.bot_ui_mandays,
                    'custom_ai_mandays': analytics_record.custom_ai_mandays,
                }
                return result
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error looking up calculation: {e}")
            return None

def display_calculation_details(calculation_data):
    """
    Display calculation details in a user-friendly format
    
    Args:
        calculation_data (dict): Calculation data from lookup
    """
    if not calculation_data:
        print("❌ No calculation found with that ID")
        return
    
    print("\n" + "="*80)
    print(f"�� CALCULATION DETAILS - ID: {calculation_data['calculation_id']}")
    print("="*80)
    
    # Basic Information
    print(f"📅 Timestamp: {calculation_data['timestamp']}")
    print(f"�� User: {calculation_data['user_name']}")
    print(f"🌍 Country: {calculation_data['country']}")
    if calculation_data['region']:
        print(f"📍 Region: {calculation_data['region']}")
    print(f"💱 Currency: {calculation_data['currency']}")
    print(f"🛣️  Route: {calculation_data['calculation_route']}")
    
    print("\n📊 INPUT VOLUMES:")
    if calculation_data['ai_volume']:
        print(f"   AI Messages: {calculation_data['ai_volume']:,.0f}")
    if calculation_data['advanced_volume']:
        print(f"   Advanced Messages: {calculation_data['advanced_volume']:,.0f}")
    if calculation_data['basic_marketing_volume']:
        print(f"   Marketing Messages: {calculation_data['basic_marketing_volume']:,.0f}")
    if calculation_data['basic_utility_volume']:
        print(f"   Utility Messages: {calculation_data['basic_utility_volume']:,.0f}")
    if calculation_data['committed_amount']:
        print(f"   Committed Amount: ${calculation_data['committed_amount']:,.2f}")
    
    print("\n💰 PRICING:")
    if calculation_data['ai_price']:
        print(f"   AI Price: ${calculation_data['ai_price']:.4f}")
    if calculation_data['advanced_price']:
        print(f"   Advanced Price: ${calculation_data['advanced_price']:.4f}")
    if calculation_data['basic_marketing_price']:
        print(f"   Marketing Price: ${calculation_data['basic_marketing_price']:.4f}")
    if calculation_data['basic_utility_price']:
        print(f"   Utility Price: ${calculation_data['basic_utility_price']:.4f}")
    if calculation_data['platform_fee']:
        print(f"   Platform Fee: ${calculation_data['platform_fee']:,.2f}")
    
    print("\n🏢 RATE CARD PRICES:")
    if calculation_data['ai_rate_card_price']:
        print(f"   AI Rate Card: ${calculation_data['ai_rate_card_price']:.4f}")
    if calculation_data['advanced_rate_card_price']:
        print(f"   Advanced Rate Card: ${calculation_data['advanced_rate_card_price']:.4f}")
    if calculation_data['basic_marketing_rate_card_price']:
        print(f"   Marketing Rate Card: ${calculation_data['basic_marketing_rate_card_price']:.4f}")
    if calculation_data['basic_utility_rate_card_price']:
        print(f"   Utility Rate Card: ${calculation_data['basic_utility_rate_card_price']:.4f}")
    
    print("\n👨‍�� MANDAY INFORMATION:")
    if calculation_data['bot_ui_manday_rate']:
        print(f"   Bot UI Rate: ${calculation_data['bot_ui_manday_rate']:,.2f}")
    if calculation_data['custom_ai_manday_rate']:
        print(f"   Custom AI Rate: ${calculation_data['custom_ai_manday_rate']:,.2f}")
    if calculation_data['bot_ui_mandays']:
        print(f"   Bot UI Mandays: {calculation_data['bot_ui_mandays']:.1f}")
    if calculation_data['custom_ai_mandays']:
        print(f"   Custom AI Mandays: {calculation_data['custom_ai_mandays']:.1f}")
    
    print("="*80)

def search_calculations_by_user(user_name):
    """
    Search for all calculations by a specific user
    
    Args:
        user_name (str): Name of the user to search for
        
    Returns:
        list: List of calculation IDs for that user
    """
    with app.app_context():
        try:
            user_calculations = Analytics.query.filter_by(user_name=user_name).all()
            results = []
            
            for calc in user_calculations:
                results.append({
                    'calculation_id': calc.calculation_id,
                    'timestamp': calc.timestamp.strftime('%Y-%m-%d %H:%M:%S') if calc.timestamp else 'N/A',
                    'country': calc.country,
                    'platform_fee': calc.platform_fee,
                    'currency': calc.currency
                })
            
            return results
            
        except Exception as e:
            print(f"❌ Error searching for user calculations: {e}")
            return []

def main():
    """Main function for interactive lookup"""
    print("�� Pricing Calculator - User Support Lookup Tool")
    print("="*50)
    
    while True:
        print("\nOptions:")
        print("1. Look up calculation by ID")
        print("2. Search calculations by user name")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            calc_id = input("Enter calculation ID: ").strip()
            if calc_id:
                result = lookup_calculation_by_id(calc_id)
                display_calculation_details(result)
            else:
                print("❌ Please enter a calculation ID")
                
        elif choice == '2':
            user_name = input("Enter user name: ").strip()
            if user_name:
                results = search_calculations_by_user(user_name)
                if results:
                    print(f"\n�� Found {len(results)} calculations for user '{user_name}':")
                    for i, calc in enumerate(results, 1):
                        print(f"   {i}. ID: {calc['calculation_id'][:8]}... | {calc['timestamp']} | {calc['country']} | ${calc['platform_fee']:,.2f} {calc['currency']}")
                else:
                    print(f"❌ No calculations found for user '{user_name}'")
            else:
                print("❌ Please enter a user name")
                
        elif choice == '3':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()

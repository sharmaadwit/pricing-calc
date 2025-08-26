#!/usr/bin/env python3
"""
Centralized Logging Configuration for Pricing Calculator
Provides clean, structured logging with different levels and formatting
"""

import logging
import sys
from datetime import datetime
import os

# Color codes for terminal output
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and better structure"""

    COLORS = {
        'DEBUG': Colors.GRAY,
        'INFO': Colors.GREEN,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.MAGENTA
    }

    def format(self, record):
        # Add timestamp
        timestamp = datetime.now().strftime('%H:%M:%S')

        # Color the level name
        level_color = self.COLORS.get(record.levelname, Colors.WHITE)
        colored_level = f"{level_color}{record.levelname:8}{Colors.RESET}"

        # Format the message with better structure
        if record.levelname == 'DEBUG':
            # Debug messages get a more compact format
            message = f"{Colors.GRAY}[{timestamp}] {colored_level} {record.getMessage()}{Colors.RESET}"
        elif record.levelname == 'INFO':
            # Info messages get a clean format
            message = f"{Colors.GREEN}[{timestamp}] {colored_level} {record.getMessage()}{Colors.RESET}"
        elif record.levelname == 'WARNING':
            # Warning messages get attention
            message = f"{Colors.YELLOW}[{timestamp}] {colored_level} ⚠️  {record.getMessage()}{Colors.RESET}"
        elif record.levelname == 'ERROR':
            # Error messages get prominent display
            message = f"{Colors.RED}[{timestamp}] {colored_level} ❌ {record.getMessage()}{Colors.RESET}"
        else:
            # Default format
            message = f"[{timestamp}] {colored_level} {record.getMessage()}"

        return message

def setup_logging(log_level='INFO', log_file=None):
    """
    Setup centralized logging configuration

    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str): Optional log file path
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    # Use colored formatter for console
    console_formatter = ColoredFormatter()
    console_handler.setFormatter(console_formatter)

    # Add console handler
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # File formatter (no colors, more detailed)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)

        logger.addHandler(file_handler)

    return logger

def get_logger(name):
    """Get a logger instance with the given name"""
    return logging.getLogger(name)

# Convenience functions for common logging patterns
def log_calculation_start(logger, calculation_id, country, volumes):
    """Log the start of a pricing calculation"""
    logger.info(f"🚀 Starting calculation {calculation_id[:8]}...")
    logger.info(f"   Country: {country}")
    logger.info(f"   Volumes: AI={volumes.get('ai', 0):,}, Adv={volumes.get('advanced', 0):,}, "
                f"Mkt={volumes.get('marketing', 0):,}, Util={volumes.get('utility', 0):,}")

def log_calculation_success(logger, results):
    """Log successful calculation results"""
    logger.info(f"✅ Calculation completed successfully")
    logger.info(f"   Revenue: ${results.get('revenue', 0):,.2f}")
    logger.info(f"   Platform Fee: ${results.get('platform_fee', 0):,.2f}")
    logger.info(f"   Margin: {results.get('margin', 'N/A')}")

def log_calculation_error(logger, error, context=""):
    """Log calculation errors"""
    logger.error(f"❌ Calculation failed: {error}")
    if context:
        logger.error(f"   Context: {context}")

def log_session_info(logger, session_data, step):
    """Log session information in a clean format"""
    logger.debug(f"📋 Session Info - Step: {step}")
    if 'calculation_id' in session_data:
        logger.debug(f"   Calculation ID: {session_data['calculation_id'][:8]}...")
    if 'inputs' in session_data and 'country' in session_data['inputs']:
        logger.debug(f"   Country: {session_data['inputs']['country']}")
    if 'inputs' in session_data and 'user_name' in session_data['inputs']:
        logger.debug(f"   User: {session_data['inputs']['user_name']}")

def log_pricing_details(logger, pricing_data):
    """Log pricing details in a structured way"""
    logger.debug(f"💰 Pricing Details:")
    for msg_type, price in pricing_data.items():
        if price is not None and price != 0:
            logger.debug(f"   {msg_type}: ${price:.4f}")

def log_meta_costs(logger, meta_costs, country):
    """Log meta costs for a country"""
    logger.debug(f"🔧 Meta Costs for {country}:")
    for cost_type, cost in meta_costs.items():
        if cost > 0:
            logger.debug(f"   {cost_type}: ${cost:.4f}")

def log_volume_breakdown(logger, volumes):
    """Log volume breakdown"""
    logger.debug(f"📊 Volume Breakdown:")
    for msg_type, volume in volumes.items():
        if volume > 0:
            logger.debug(f"   {msg_type}: {volume:,} messages")

def log_platform_fee(logger, platform_fee, currency="$"):
    """Log platform fee information"""
    logger.info(f"🏢 Platform Fee: {currency}{platform_fee:,.2f}")

def log_manday_costs(logger, manday_rates, manday_breakdown):
    """Log manday cost information"""
    logger.debug(f"👨‍💻 Manday Costs:")
    logger.debug(f"   Bot UI Rate: ${manday_rates.get('bot_ui', 0):,.2f}")
    logger.debug(f"   Custom AI Rate: ${manday_rates.get('custom_ai', 0):,.2f}")
    logger.debug(f"   Bot UI Mandays: {manday_breakdown.get('bot_ui', 0):.1f}")
    logger.debug(f"   Custom AI Mandays: {manday_breakdown.get('custom_ai', 0):.1f}")

# New functions for user support and calculation tracking
def log_calculation_inputs(logger, calculation_id, inputs, pricing_inputs=None):
    """Log complete calculation inputs for user support"""
    logger.info(f"�� CALCULATION INPUTS - ID: {calculation_id[:8]}...")
    logger.info(f"   User: {inputs.get('user_name', 'N/A')}")
    logger.info(f"   Country: {inputs.get('country', 'N/A')}")
    logger.info(f"   Region: {inputs.get('region', 'N/A')}")
    logger.info(f"   Volumes:")
    logger.info(f"     AI: {inputs.get('ai_volume', 0):,}")
    logger.info(f"     Advanced: {inputs.get('advanced_volume', 0):,}")
    logger.info(f"     Marketing: {inputs.get('basic_marketing_volume', 0):,}")
    logger.info(f"     Utility: {inputs.get('basic_utility_volume', 0):,}")
    
    if pricing_inputs:
        logger.info(f"   Pricing:")
        logger.info(f"     AI Price: ${pricing_inputs.get('ai_price', 0):.4f}")
        logger.info(f"     Advanced Price: ${pricing_inputs.get('advanced_price', 0):.4f}")
        logger.info(f"     Marketing Price: ${pricing_inputs.get('basic_marketing_price', 0):.4f}")
        logger.info(f"     Utility Price: ${pricing_inputs.get('basic_utility_price', 0):.4f}")
        logger.info(f"     Platform Fee: ${pricing_inputs.get('platform_fee', 0):,.2f}")

def log_calculation_results(logger, calculation_id, results, inputs=None):
    """Log complete calculation results for user support"""
    logger.info(f"💰 CALCULATION RESULTS - ID: {calculation_id[:8]}...")
    logger.info(f"   Revenue: ${results.get('revenue', 0):,.2f}")
    logger.info(f"   Platform Fee: ${results.get('platform_fee', 0):,.2f}")
    logger.info(f"   Total Costs: ${results.get('total_costs', 0):,.2f}")
    logger.info(f"   Margin: {results.get('margin', 'N/A')}")
    
    if 'line_items' in results:
        logger.info(f"   Line Items:")
        for item in results['line_items']:
            if isinstance(item, dict) and 'label' in item:
                volume = item.get('volume', 0)
                revenue = item.get('revenue', 0)
                if volume > 0 or revenue > 0:
                    logger.info(f"     {item['label']}: {volume:,} msgs, ${revenue:,.2f}")

def log_calculation_summary(logger, calculation_id, inputs, results, pricing_inputs=None):
    """Log a complete calculation summary for easy user support lookup"""
    logger.info(f"🔍 CALCULATION SUMMARY - ID: {calculation_id}")
    logger.info(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"   User: {inputs.get('user_name', 'N/A')}")
    logger.info(f"   Country: {inputs.get('country', 'N/A')}")
    logger.info(f"   Total Revenue: ${results.get('revenue', 0):,.2f}")
    logger.info(f"   Platform Fee: ${results.get('platform_fee', 0):,.2f}")
    logger.info(f"   Margin: {results.get('margin', 'N/A')}")
    logger.info(f"   Calculation Route: {'Bundle' if inputs.get('committed_amount') else 'Volumes'}")
    logger.info(f"   --- END CALCULATION {calculation_id[:8]}... ---")

def log_user_support_lookup(logger, calculation_id, lookup_result):
    """Log when someone looks up a calculation for user support"""
    if lookup_result:
        logger.info(f"🔍 USER SUPPORT LOOKUP - ID: {calculation_id}")
        logger.info(f"   Found calculation for user: {lookup_result.get('user_name', 'N/A')}")
        logger.info(f"   Country: {lookup_result.get('country', 'N/A')}")
        logger.info(f"   Revenue: ${lookup_result.get('platform_fee', 0):,.2f}")
        logger.info(f"   Timestamp: {lookup_result.get('timestamp', 'N/A')}")
    else:
        logger.warning(f"⚠️  USER SUPPORT LOOKUP FAILED - ID: {calculation_id} not found")

# Enhanced error logging for debugging 500 errors
def log_application_error(logger, error, user_info=None, calculation_id=None, request_data=None):
    """Log application errors with detailed context for debugging"""
    logger.error(f"💥 APPLICATION ERROR OCCURRED")
    logger.error(f"   Error Type: {type(error).__name__}")
    logger.error(f"   Error Message: {str(error)}")
    
    if user_info:
        logger.error(f"   User: {user_info.get('user_name', 'Unknown')}")
        logger.error(f"   Country: {user_info.get('country', 'Unknown')}")
    
    if calculation_id:
        logger.error(f"   Calculation ID: {calculation_id[:8]}...")
    
    if request_data:
        logger.error(f"   Request Step: {request_data.get('step', 'Unknown')}")
        logger.error(f"   Request Method: {request_data.get('method', 'Unknown')}")
    
    # Log the full traceback for debugging
    import traceback
    logger.error(f"   Full Traceback:")
    for line in traceback.format_exc().split('\n'):
        if line.strip():
            logger.error(f"     {line}")

def log_http_error(logger, status_code, error_message, user_info=None, calculation_id=None, request_path=None):
    """Log HTTP errors (like 500) with context"""
    if status_code >= 500:
        logger.error(f"🚨 SERVER ERROR {status_code}")
        logger.error(f"   Path: {request_path or 'Unknown'}")
        logger.error(f"   Error: {error_message}")
        
        if user_info:
            logger.error(f"   User: {user_info.get('user_name', 'Unknown')}")
            logger.error(f"   Country: {user_info.get('country', 'Unknown')}")
        
        if calculation_id:
            logger.error(f"   Calculation ID: {calculation_id[:8]}...")
        
        logger.error(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    elif status_code >= 400:
        logger.warning(f"⚠️  CLIENT ERROR {status_code}")
        logger.warning(f"   Path: {request_path or 'Unknown'}")
        logger.warning(f"   Error: {error_message}")

def log_request_context(logger, request, session_data=None):
    """Log request context for debugging"""
    logger.debug(f"�� REQUEST CONTEXT")
    logger.debug(f"   Method: {request.method}")
    logger.debug(f"   Path: {request.path}")
    logger.debug(f"   User Agent: {request.headers.get('User-Agent', 'Unknown')}")
    logger.debug(f"   Remote IP: {request.remote_addr}")
    
    if session_data:
        logger.debug(f"   Session User: {session_data.get('user_name', 'Not logged in')}")
        logger.debug(f"   Calculation ID: {session_data.get('calculation_id', 'None')[:8] if session_data.get('calculation_id') else 'None'}...")
    
    if request.form:
        logger.debug(f"   Form Data: {len(request.form)} fields")
        for key, value in list(request.form.items())[:5]:  # Log first 5 fields
            logger.debug(f"     {key}: {value}")
        if len(request.form) > 5:
            logger.debug(f"     ... and {len(request.form) - 5} more fields")

# Initialize default logging
if __name__ == "__main__":
    # Test the logging system
    logger = setup_logging('INFO')
    logger.info("🧪 Testing the new clean logging system...")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

# Voice Channel Pricing Implementation Plan

## Overview
This document outlines the implementation steps to add voice channel pricing to the existing pricing calculator. After implementation, users will be able to generate prices for:
1. **Text only** (current functionality - unchanged)
2. **Voice only** (new functionality)
3. **Text + Voice** (new functionality)

## Current Architecture Analysis

### Current Flow:
1. **Volumes Form**: User enters message volumes (AI, Advanced, Marketing, Utility)
2. **Prices Form**: User reviews/edits suggested prices (rate card pricing)
3. **Results**: Display final pricing with breakdown

### Current Pricing Components:
- Message volumes (AI, Advanced, Marketing, Utility)
- Platform fees (calculated based on features)
- One-time dev costs (mandays × rates)
- Voice Notes (optional, per-minute billing on actuals)

## Voice Channel Pricing Components (from Image)

Based on the provided pricing sheet, we need to implement:

### 1. Dev Effort For Voice Bots/WhatsApp Voice
- **1 Journey (Voice AI FAQ/Lead Gen/Support Bot Build)**: 3 mandays
- **Each API integration**: 1 manday
- **Each additional language above Hindi and English**: 30% of effort
- **Agent Handover - PSTN**: 
  - To Knowlarity: 1 manday
  - Any Platform except Knowlarity: 5 mandays
- **WhatsApp Voice**:
  - To Knowlarity: 1 manday
  - Any Platform except Knowlarity: 5 mandays (with 50,000 INR one-time setup fee)

### 2. Platform Fee For Voice AI
- **Voice AI Platform Fee**: 150,000 INR (0 if text AI is already selected)
- **Knowlarity Platform - For Agent Handover**: 25,000 INR
- **Virtual Number**: 500 INR

### 3. PSTN Calling Charges (India)
- **Inbound AI**: 
  - Pre-committed bundled: 4.5 INR/minute
  - Overage: 6.00 INR/minute
- **Outbound AI**:
  - Pre-committed bundled: 4.8 INR/minute
  - Overage: 6.00 INR/minute
- **Manual C2C call (Human Agent)**:
  - Pre-committed bundled: 0.55 INR/minute
  - Overage: 0.6 INR/minute

### 4. WhatsApp Voice Calling Charges (India)
Volume-based tiered pricing:
- **Up to 50,000 minutes**: Outbound 0.49 INR/min, Inbound 0.06 INR/min
- **50,001 to 250,000 minutes**: Outbound 0.35 INR/min, Inbound 0.05 INR/min
- **250,001 to 1,000,000 minutes**: Outbound 0.22 INR/min, Inbound 0.04 INR/min
- **1,000,001 to 2,500,000 minutes**: Outbound 0.16 INR/min, Inbound 0.03 INR/min
- **2,500,001 to 5,000,000 minutes**: Outbound 0.11 INR/min, Inbound 0.02 INR/min
- **5,000,001+ minutes**: Outbound 0.07 INR/min, Inbound 0.02 INR/min

## Implementation Steps

### Step 1: Add Voice Channel Configuration to `pricing_config.py`

**Location**: After line 376 (after `PLATFORM_PRICING_GUIDANCE`)

Add the following configuration dictionaries:

```python
# =============================================================================
# VOICE CHANNEL PRICING CONFIGURATION (India)
# =============================================================================

# Voice Bot Development Effort (Mandays)
VOICE_DEV_EFFORT = {
    'journey': 3,  # 1 Journey (Voice AI FAQ/Lead Gen/Support Bot Build)
    'api_integration': 1,  # Each API integration
    'additional_language_multiplier': 0.30,  # 30% of effort for each additional language above Hindi and English
    'agent_handover_pstn_knowlarity': 1,
    'agent_handover_pstn_other': 5,
    'whatsapp_voice_knowlarity': 1,
    'whatsapp_voice_other': 5,
    'whatsapp_voice_setup_fee_other': 50000,  # One-time setup fee for non-Knowlarity platforms
}

# Voice Platform Fees (INR)
VOICE_PLATFORM_FEES = {
    'voice_ai': 150000,  # 0 if text AI is already selected
    'knowlarity_platform': 25000,  # For Agent Handover
    'virtual_number': 500,
}

# PSTN Calling Charges (INR per minute)
PSTN_CALLING_CHARGES = {
    'inbound_ai': {
        'bundled': 4.5,
        'overage': 6.00
    },
    'outbound_ai': {
        'bundled': 4.8,
        'overage': 6.00
    },
    'manual_c2c': {
        'bundled': 0.55,
        'overage': 0.6
    }
}

# WhatsApp Voice Calling Charges (INR per minute) - Volume-based tiers
WHATSAPP_VOICE_CHARGES = {
    'India': [
        {
            'min_minutes': 0,
            'max_minutes': 50000,
            'outbound': 0.49,
            'inbound': 0.06,
            'meta_rate': 0.3885,
            'gupshup_margin_pct': 25
        },
        {
            'min_minutes': 50001,
            'max_minutes': 250000,
            'outbound': 0.35,
            'inbound': 0.05,
            'meta_rate': 0.2785,
            'gupshup_margin_pct': 25
        },
        {
            'min_minutes': 250001,
            'max_minutes': 1000000,
            'outbound': 0.22,
            'inbound': 0.04,
            'meta_rate': 0.1759,
            'gupshup_margin_pct': 25
        },
        {
            'min_minutes': 1000001,
            'max_minutes': 2500000,
            'outbound': 0.16,
            'inbound': 0.03,
            'meta_rate': 0.1319,
            'gupshup_margin_pct': 25
        },
        {
            'min_minutes': 2500001,
            'max_minutes': 5000000,
            'outbound': 0.11,
            'inbound': 0.02,
            'meta_rate': 0.0880,
            'gupshup_margin_pct': 25
        },
        {
            'min_minutes': 5000001,
            'max_minutes': float('inf'),
            'outbound': 0.07,
            'inbound': 0.02,
            'meta_rate': 0.0586,
            'gupshup_margin_pct': 25
        }
    ]
}

def get_whatsapp_voice_rate(country, minutes, call_type='outbound'):
    """
    Get WhatsApp voice rate based on volume tier.
    
    Args:
        country: Country name (currently only 'India' supported)
        minutes: Total minutes in the tier
        call_type: 'outbound' or 'inbound'
    
    Returns:
        float: Rate per minute
    """
    if country != 'India':
        # Fallback to highest tier for other countries (can be expanded later)
        tier = WHATSAPP_VOICE_CHARGES['India'][-1]
        return tier[call_type]
    
    tiers = WHATSAPP_VOICE_CHARGES.get(country, WHATSAPP_VOICE_CHARGES['India'])
    for tier in tiers:
        if tier['min_minutes'] <= minutes <= tier['max_minutes']:
            return tier[call_type]
    
    # Fallback to highest tier
    return tiers[-1][call_type]
```

### Step 2: Update `calculator.py` - Add Voice Channel Calculation Functions

**Location**: After the existing `calculate_pricing` function (around line 205)

Add these new functions:

```python
def calculate_voice_dev_mandays(inputs):
    """
    Calculate total mandays for voice bot development.
    
    Args:
        inputs: Dictionary with voice-related inputs
    
    Returns:
        int: Total mandays for voice development
    """
    total_mandays = 0
    
    # Journeys
    num_voice_journeys = int(inputs.get('num_voice_journeys', 0) or 0)
    total_mandays += num_voice_journeys * VOICE_DEV_EFFORT['journey']
    
    # API integrations
    num_voice_apis = int(inputs.get('num_voice_apis', 0) or 0)
    total_mandays += num_voice_apis * VOICE_DEV_EFFORT['api_integration']
    
    # Additional languages
    num_additional_languages = int(inputs.get('num_additional_voice_languages', 0) or 0)
    if num_additional_languages > 0:
        base_effort = total_mandays  # Current effort before language multiplier
        additional_effort = base_effort * VOICE_DEV_EFFORT['additional_language_multiplier'] * num_additional_languages
        total_mandays += additional_effort
    
    # Agent Handover - PSTN
    agent_handover_pstn = inputs.get('agent_handover_pstn', 'None')
    if agent_handover_pstn == 'Knowlarity':
        total_mandays += VOICE_DEV_EFFORT['agent_handover_pstn_knowlarity']
    elif agent_handover_pstn == 'Other':
        total_mandays += VOICE_DEV_EFFORT['agent_handover_pstn_other']
    
    # WhatsApp Voice
    whatsapp_voice_platform = inputs.get('whatsapp_voice_platform', 'None')
    if whatsapp_voice_platform == 'Knowlarity':
        total_mandays += VOICE_DEV_EFFORT['whatsapp_voice_knowlarity']
    elif whatsapp_voice_platform == 'Other':
        total_mandays += VOICE_DEV_EFFORT['whatsapp_voice_other']
    
    return total_mandays

def calculate_voice_platform_fee(inputs, has_text_ai=False):
    """
    Calculate voice platform fees.
    
    Args:
        inputs: Dictionary with voice-related inputs
        has_text_ai: Boolean indicating if text AI is already selected
    
    Returns:
        float: Total voice platform fee in INR
    """
    total_fee = 0
    
    # Voice AI platform fee (0 if text AI already selected)
    if inputs.get('voice_ai_enabled', 'No') == 'Yes':
        if not has_text_ai:
            total_fee += VOICE_PLATFORM_FEES['voice_ai']
    
    # Knowlarity platform for agent handover
    if inputs.get('agent_handover_pstn', 'None') == 'Knowlarity':
        total_fee += VOICE_PLATFORM_FEES['knowlarity_platform']
    
    # Virtual number
    if inputs.get('virtual_number_required', 'No') == 'Yes':
        total_fee += VOICE_PLATFORM_FEES['virtual_number']
    
    return total_fee

def calculate_voice_calling_costs(inputs, country='India'):
    """
    Calculate voice calling costs (PSTN and WhatsApp).
    
    Args:
        inputs: Dictionary with voice volume inputs
        country: Country name
    
    Returns:
        dict: Dictionary with cost breakdown
    """
    costs = {
        'pstn_inbound_ai': 0,
        'pstn_outbound_ai': 0,
        'pstn_manual_c2c': 0,
        'whatsapp_voice_outbound': 0,
        'whatsapp_voice_inbound': 0,
        'total': 0
    }
    
    # PSTN Calling Charges
    pstn_inbound_ai_minutes = float(inputs.get('pstn_inbound_ai_minutes', 0) or 0)
    pstn_outbound_ai_minutes = float(inputs.get('pstn_outbound_ai_minutes', 0) or 0)
    pstn_manual_minutes = float(inputs.get('pstn_manual_minutes', 0) or 0)
    
    # Get bundled and overage thresholds (user would specify committed minutes)
    pstn_inbound_committed = float(inputs.get('pstn_inbound_committed', 0) or 0)
    pstn_outbound_committed = float(inputs.get('pstn_outbound_committed', 0) or 0)
    pstn_manual_committed = float(inputs.get('pstn_manual_committed', 0) or 0)
    
    # Calculate bundled vs overage
    if pstn_inbound_ai_minutes > 0:
        bundled_minutes = min(pstn_inbound_ai_minutes, pstn_inbound_committed)
        overage_minutes = max(0, pstn_inbound_ai_minutes - pstn_inbound_committed)
        costs['pstn_inbound_ai'] = (bundled_minutes * PSTN_CALLING_CHARGES['inbound_ai']['bundled'] +
                                   overage_minutes * PSTN_CALLING_CHARGES['inbound_ai']['overage'])
    
    if pstn_outbound_ai_minutes > 0:
        bundled_minutes = min(pstn_outbound_ai_minutes, pstn_outbound_committed)
        overage_minutes = max(0, pstn_outbound_ai_minutes - pstn_outbound_committed)
        costs['pstn_outbound_ai'] = (bundled_minutes * PSTN_CALLING_CHARGES['outbound_ai']['bundled'] +
                                    overage_minutes * PSTN_CALLING_CHARGES['outbound_ai']['overage'])
    
    if pstn_manual_minutes > 0:
        bundled_minutes = min(pstn_manual_minutes, pstn_manual_committed)
        overage_minutes = max(0, pstn_manual_minutes - pstn_manual_committed)
        costs['pstn_manual_c2c'] = (bundled_minutes * PSTN_CALLING_CHARGES['manual_c2c']['bundled'] +
                                   overage_minutes * PSTN_CALLING_CHARGES['manual_c2c']['overage'])
    
    # WhatsApp Voice Calling Charges
    whatsapp_outbound_minutes = float(inputs.get('whatsapp_voice_outbound_minutes', 0) or 0)
    whatsapp_inbound_minutes = float(inputs.get('whatsapp_voice_inbound_minutes', 0) or 0)
    total_whatsapp_minutes = whatsapp_outbound_minutes + whatsapp_inbound_minutes
    
    if whatsapp_outbound_minutes > 0:
        outbound_rate = get_whatsapp_voice_rate(country, total_whatsapp_minutes, 'outbound')
        costs['whatsapp_voice_outbound'] = whatsapp_outbound_minutes * outbound_rate
    
    if whatsapp_inbound_minutes > 0:
        inbound_rate = get_whatsapp_voice_rate(country, total_whatsapp_minutes, 'inbound')
        costs['whatsapp_voice_inbound'] = whatsapp_inbound_minutes * inbound_rate
    
    costs['total'] = (costs['pstn_inbound_ai'] + costs['pstn_outbound_ai'] + costs['pstn_manual_c2c'] +
                     costs['whatsapp_voice_outbound'] + costs['whatsapp_voice_inbound'])
    
    return costs

def calculate_voice_pricing(inputs, country='India', has_text_ai=False):
    """
    Calculate complete voice channel pricing.
    
    Args:
        inputs: Dictionary with all voice-related inputs
        country: Country name
        has_text_ai: Boolean indicating if text AI is already selected
    
    Returns:
        dict: Complete voice pricing breakdown
    """
    # Development costs
    voice_mandays = calculate_voice_dev_mandays(inputs)
    manday_rate = COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['APAC'])
    # Use custom_ai rate for voice development (voice is AI-related)
    voice_dev_cost = voice_mandays * manday_rate.get('custom_ai', manday_rate.get('bot_ui', 30000))
    
    # Add WhatsApp setup fee if applicable
    whatsapp_setup_fee = 0
    if inputs.get('whatsapp_voice_platform', 'None') == 'Other':
        whatsapp_setup_fee = VOICE_DEV_EFFORT['whatsapp_voice_setup_fee_other']
    
    # Platform fees
    voice_platform_fee = calculate_voice_platform_fee(inputs, has_text_ai)
    
    # Calling costs
    calling_costs = calculate_voice_calling_costs(inputs, country)
    
    # Total
    total_voice_cost = (voice_dev_cost + whatsapp_setup_fee + voice_platform_fee + calling_costs['total'])
    
    return {
        'voice_mandays': voice_mandays,
        'voice_dev_cost': voice_dev_cost,
        'whatsapp_setup_fee': whatsapp_setup_fee,
        'voice_platform_fee': voice_platform_fee,
        'calling_costs': calling_costs,
        'total_voice_cost': total_voice_cost,
        'breakdown': {
            'development': voice_dev_cost + whatsapp_setup_fee,
            'platform': voice_platform_fee,
            'calling': calling_costs['total']
        }
    }
```

**Import statements** to add at top of `calculator.py`:
```python
from pricing_config import (
    meta_costs_table, COUNTRY_MANDAY_RATES, ACTIVITY_MANDAYS, committed_amount_slabs,
    VOICE_DEV_EFFORT, VOICE_PLATFORM_FEES, PSTN_CALLING_CHARGES, WHATSAPP_VOICE_CHARGES,
    get_whatsapp_voice_rate
)
```

### Step 3: Update HTML Template (`templates/index.html`)

#### 3.1 Add Channel Selection in Volumes Form

**Location**: After the country selection (around line 442), add:

```html
<div class="form-group">
    <label for="channel_type">Channel Type:</label>
    <select name="channel_type" id="channel_type" onchange="toggleChannelFields()">
        <option value="text_only" {% if inputs and inputs.channel_type == 'text_only' %}selected{% endif %}>Text Only</option>
        <option value="voice_only" {% if inputs and inputs.channel_type == 'voice_only' %}selected{% endif %}>Voice Only</option>
        <option value="text_voice" {% if inputs and inputs.channel_type == 'text_voice' %}selected{% endif %}>Text + Voice</option>
    </select>
    <div class="help-text">Select the channel type for this pricing calculation</div>
</div>
```

#### 3.2 Add Voice Channel Inputs Section

**Location**: After the "Volume Estimation" section (around line 655), add:

```html
<!-- Voice Channel Section (shown only when voice is selected) -->
<div id="voice-channel-section" class="form-section" style="display: none;">
    <h2>Voice Channel Configuration</h2>
    
    <!-- Voice AI Platform -->
    <div class="form-group">
        <label for="voice_ai_enabled">Voice AI Enabled:</label>
        <select name="voice_ai_enabled" id="voice_ai_enabled">
            <option value="No" {% if inputs and inputs.voice_ai_enabled == 'No' %}selected{% endif %}>No</option>
            <option value="Yes" {% if inputs and inputs.voice_ai_enabled == 'Yes' %}selected{% endif %}>Yes</option>
        </select>
        <div class="help-text">Note: Platform fee is 0 if Text AI is already selected</div>
    </div>
    
    <!-- Voice Development Effort -->
    <div class="form-group">
        <label for="num_voice_journeys">Number of Voice Journeys:</label>
        <input type="number" name="num_voice_journeys" id="num_voice_journeys" min="0" value="{{ inputs.get('num_voice_journeys', '0') }}">
        <div class="help-text">1 Journey = 3 mandays (Voice AI FAQ/Lead Gen/Support Bot Build)</div>
    </div>
    
    <div class="form-group">
        <label for="num_voice_apis">Number of Voice API Integrations:</label>
        <input type="number" name="num_voice_apis" id="num_voice_apis" min="0" value="{{ inputs.get('num_voice_apis', '0') }}">
        <div class="help-text">Each API integration = 1 manday</div>
    </div>
    
    <div class="form-group">
        <label for="num_additional_voice_languages">Additional Languages (above Hindi and English):</label>
        <input type="number" name="num_additional_voice_languages" id="num_additional_voice_languages" min="0" value="{{ inputs.get('num_additional_voice_languages', '0') }}">
        <div class="help-text">Each additional language = 30% of base effort</div>
    </div>
    
    <!-- Agent Handover -->
    <div class="form-group">
        <label for="agent_handover_pstn">Agent Handover - PSTN:</label>
        <select name="agent_handover_pstn" id="agent_handover_pstn">
            <option value="None" {% if inputs and inputs.agent_handover_pstn == 'None' %}selected{% endif %}>None</option>
            <option value="Knowlarity" {% if inputs and inputs.agent_handover_pstn == 'Knowlarity' %}selected{% endif %}>Knowlarity (1 manday)</option>
            <option value="Other" {% if inputs and inputs.agent_handover_pstn == 'Other' %}selected{% endif %}>Other Platform (5 mandays)</option>
        </select>
    </div>
    
    <!-- WhatsApp Voice -->
    <div class="form-group">
        <label for="whatsapp_voice_platform">WhatsApp Voice Platform:</label>
        <select name="whatsapp_voice_platform" id="whatsapp_voice_platform">
            <option value="None" {% if inputs and inputs.whatsapp_voice_platform == 'None' %}selected{% endif %}>None</option>
            <option value="Knowlarity" {% if inputs and inputs.whatsapp_voice_platform == 'Knowlarity' %}selected{% endif %}>Knowlarity (1 manday)</option>
            <option value="Other" {% if inputs and inputs.whatsapp_voice_platform == 'Other' %}selected{% endif %}>Other Platform (5 mandays + ₹50,000 setup)</option>
        </select>
    </div>
    
    <div class="form-group">
        <label for="virtual_number_required">Virtual Number Required:</label>
        <select name="virtual_number_required" id="virtual_number_required">
            <option value="No" {% if inputs and inputs.virtual_number_required == 'No' %}selected{% endif %}>No</option>
            <option value="Yes" {% if inputs and inputs.virtual_number_required == 'Yes' %}selected{% endif %}>Yes (+₹500)</option>
        </select>
    </div>
    
    <!-- PSTN Calling Volumes -->
    <h3>PSTN Calling Charges (per month)</h3>
    <div class="form-group">
        <label for="pstn_inbound_ai_minutes">PSTN Inbound AI Minutes:</label>
        <input type="text" name="pstn_inbound_ai_minutes" id="pstn_inbound_ai_minutes" class="comma-number" value="{{ inputs.get('pstn_inbound_ai_minutes', '') }}">
        <div class="help-text">Bundled: ₹4.5/min, Overage: ₹6.00/min</div>
    </div>
    
    <div class="form-group">
        <label for="pstn_inbound_committed">PSTN Inbound Committed Minutes:</label>
        <input type="text" name="pstn_inbound_committed" id="pstn_inbound_committed" class="comma-number" value="{{ inputs.get('pstn_inbound_committed', '') }}">
        <div class="help-text">Pre-committed bundled minutes</div>
    </div>
    
    <div class="form-group">
        <label for="pstn_outbound_ai_minutes">PSTN Outbound AI Minutes:</label>
        <input type="text" name="pstn_outbound_ai_minutes" id="pstn_outbound_ai_minutes" class="comma-number" value="{{ inputs.get('pstn_outbound_ai_minutes', '') }}">
        <div class="help-text">Bundled: ₹4.8/min, Overage: ₹6.00/min</div>
    </div>
    
    <div class="form-group">
        <label for="pstn_outbound_committed">PSTN Outbound Committed Minutes:</label>
        <input type="text" name="pstn_outbound_committed" id="pstn_outbound_committed" class="comma-number" value="{{ inputs.get('pstn_outbound_committed', '') }}">
    </div>
    
    <div class="form-group">
        <label for="pstn_manual_minutes">PSTN Manual C2C (Human Agent) Minutes:</label>
        <input type="text" name="pstn_manual_minutes" id="pstn_manual_minutes" class="comma-number" value="{{ inputs.get('pstn_manual_minutes', '') }}">
        <div class="help-text">Bundled: ₹0.55/min, Overage: ₹0.6/min</div>
    </div>
    
    <div class="form-group">
        <label for="pstn_manual_committed">PSTN Manual Committed Minutes:</label>
        <input type="text" name="pstn_manual_committed" id="pstn_manual_committed" class="comma-number" value="{{ inputs.get('pstn_manual_committed', '') }}">
    </div>
    
    <!-- WhatsApp Voice Calling Volumes -->
    <h3>WhatsApp Voice Calling Charges (per month)</h3>
    <div class="form-group">
        <label for="whatsapp_voice_outbound_minutes">WhatsApp Voice Outbound Minutes:</label>
        <input type="text" name="whatsapp_voice_outbound_minutes" id="whatsapp_voice_outbound_minutes" class="comma-number" value="{{ inputs.get('whatsapp_voice_outbound_minutes', '') }}">
        <div class="help-text">Tiered pricing based on total minutes (outbound + inbound)</div>
    </div>
    
    <div class="form-group">
        <label for="whatsapp_voice_inbound_minutes">WhatsApp Voice Inbound Minutes:</label>
        <input type="text" name="whatsapp_voice_inbound_minutes" id="whatsapp_voice_inbound_minutes" class="comma-number" value="{{ inputs.get('whatsapp_voice_inbound_minutes', '') }}">
        <div class="help-text">Tiered pricing based on total minutes (outbound + inbound)</div>
    </div>
</div>

<script>
function toggleChannelFields() {
    const channelType = document.getElementById('channel_type').value;
    const textFields = document.querySelectorAll('.form-section:has(#ai_volume)');
    const voiceFields = document.getElementById('voice-channel-section');
    
    if (channelType === 'text_only') {
        // Show text fields, hide voice fields
        textFields.forEach(f => f.style.display = '');
        if (voiceFields) voiceFields.style.display = 'none';
    } else if (channelType === 'voice_only') {
        // Hide text fields, show voice fields
        textFields.forEach(f => f.style.display = 'none');
        if (voiceFields) voiceFields.style.display = '';
    } else if (channelType === 'text_voice') {
        // Show both
        textFields.forEach(f => f.style.display = '');
        if (voiceFields) voiceFields.style.display = '';
    }
}

// Call on page load
document.addEventListener('DOMContentLoaded', function() {
    toggleChannelFields();
});
</script>
```

### Step 4: Update `app.py` to Handle Voice Channel

#### 4.1 Update Volumes Handler

**Location**: In the `step == 'volumes'` section (around line 437), add voice fields to session:

```python
# Voice channel fields
channel_type = request.form.get('channel_type', 'text_only')
voice_ai_enabled = request.form.get('voice_ai_enabled', 'No')
num_voice_journeys = request.form.get('num_voice_journeys', '0')
num_voice_apis = request.form.get('num_voice_apis', '0')
num_additional_voice_languages = request.form.get('num_additional_voice_languages', '0')
agent_handover_pstn = request.form.get('agent_handover_pstn', 'None')
whatsapp_voice_platform = request.form.get('whatsapp_voice_platform', 'None')
virtual_number_required = request.form.get('virtual_number_required', 'No')
pstn_inbound_ai_minutes = parse_volume(request.form.get('pstn_inbound_ai_minutes', ''))
pstn_inbound_committed = parse_volume(request.form.get('pstn_inbound_committed', ''))
pstn_outbound_ai_minutes = parse_volume(request.form.get('pstn_outbound_ai_minutes', ''))
pstn_outbound_committed = parse_volume(request.form.get('pstn_outbound_committed', ''))
pstn_manual_minutes = parse_volume(request.form.get('pstn_manual_minutes', ''))
pstn_manual_committed = parse_volume(request.form.get('pstn_manual_committed', ''))
whatsapp_voice_outbound_minutes = parse_volume(request.form.get('whatsapp_voice_outbound_minutes', ''))
whatsapp_voice_inbound_minutes = parse_volume(request.form.get('whatsapp_voice_inbound_minutes', ''))

# Add to session['inputs']
session['inputs'].update({
    'channel_type': channel_type,
    'voice_ai_enabled': voice_ai_enabled,
    'num_voice_journeys': num_voice_journeys,
    'num_voice_apis': num_voice_apis,
    'num_additional_voice_languages': num_additional_voice_languages,
    'agent_handover_pstn': agent_handover_pstn,
    'whatsapp_voice_platform': whatsapp_voice_platform,
    'virtual_number_required': virtual_number_required,
    'pstn_inbound_ai_minutes': pstn_inbound_ai_minutes,
    'pstn_inbound_committed': pstn_inbound_committed,
    'pstn_outbound_ai_minutes': pstn_outbound_ai_minutes,
    'pstn_outbound_committed': pstn_outbound_committed,
    'pstn_manual_minutes': pstn_manual_minutes,
    'pstn_manual_committed': pstn_manual_committed,
    'whatsapp_voice_outbound_minutes': whatsapp_voice_outbound_minutes,
    'whatsapp_voice_inbound_minutes': whatsapp_voice_inbound_minutes,
})
```

#### 4.2 Update Prices Handler

**Location**: In the `step == 'prices'` section (around line 538), add voice pricing calculations:

```python
# Check if voice channel is enabled
channel_type = inputs.get('channel_type', 'text_only')
has_text_ai = channel_type in ['text_only', 'text_voice'] and float(inputs.get('ai_volume', 0) or 0) > 0
has_voice = channel_type in ['voice_only', 'text_voice']

# Calculate voice pricing if voice is enabled
voice_pricing = None
if has_voice:
    from calculator import calculate_voice_pricing
    voice_pricing = calculate_voice_pricing(inputs, country=inputs.get('country', 'India'), has_text_ai=has_text_ai)
    session['voice_pricing'] = voice_pricing
```

#### 4.3 Update Results Handler

**Location**: In the results rendering section (around line 842), include voice pricing in results:

```python
# Include voice pricing in results if applicable
voice_pricing = session.get('voice_pricing')
if voice_pricing:
    results['voice_pricing'] = voice_pricing
    # Update total revenue to include voice costs
    results['revenue'] = results.get('revenue', 0) + voice_pricing['total_voice_cost']
```

### Step 5: Update Results Template Section

**Location**: In the results section of `index.html` (around line 862), add voice pricing display:

```html
{% if voice_pricing %}
<div style="background: #fff3e0; border: 1px solid #ffb74d; border-radius: 8px; padding: 18px 28px; margin-bottom: 28px;">
    <h3 style="margin-top:0;">Voice Channel Pricing</h3>
    <table style="border-collapse: collapse; width: 100%; font-size: 1.05em;">
        <tr>
            <td><b>Voice Development ({{ voice_pricing.voice_mandays }} mandays)</b></td>
            <td style="text-align:right;">{{ currency_symbol }}{{ voice_pricing.voice_dev_cost|int }}</td>
        </tr>
        {% if voice_pricing.whatsapp_setup_fee > 0 %}
        <tr>
            <td><b>WhatsApp Setup Fee</b></td>
            <td style="text-align:right;">{{ currency_symbol }}{{ voice_pricing.whatsapp_setup_fee|int }}</td>
        </tr>
        {% endif %}
        <tr>
            <td><b>Voice Platform Fee</b></td>
            <td style="text-align:right;">{{ currency_symbol }}{{ voice_pricing.voice_platform_fee|int }}</td>
        </tr>
        <tr>
            <td><b>PSTN Inbound AI</b></td>
            <td style="text-align:right;">{{ currency_symbol }}{{ voice_pricing.calling_costs.pstn_inbound_ai|int }}</td>
        </tr>
        <tr>
            <td><b>PSTN Outbound AI</b></td>
            <td style="text-align:right;">{{ currency_symbol }}{{ voice_pricing.calling_costs.pstn_outbound_ai|int }}</td>
        </tr>
        <tr>
            <td><b>PSTN Manual C2C</b></td>
            <td style="text-align:right;">{{ currency_symbol }}{{ voice_pricing.calling_costs.pstn_manual_c2c|int }}</td>
        </tr>
        <tr>
            <td><b>WhatsApp Voice Outbound</b></td>
            <td style="text-align:right;">{{ currency_symbol }}{{ voice_pricing.calling_costs.whatsapp_voice_outbound|int }}</td>
        </tr>
        <tr>
            <td><b>WhatsApp Voice Inbound</b></td>
            <td style="text-align:right;">{{ currency_symbol }}{{ voice_pricing.calling_costs.whatsapp_voice_inbound|int }}</td>
        </tr>
        <tr style="background: #e3f2fd; border-top: 2px solid #2196f3;">
            <td><b>Total Voice Cost</b></td>
            <td style="text-align:right; font-weight: bold; font-size: 1.2em;">{{ currency_symbol }}{{ voice_pricing.total_voice_cost|int }}</td>
        </tr>
    </table>
</div>
{% endif %}
```

## Testing Checklist

### Test Cases:

1. **Text Only** (existing functionality)
   - ✅ Should work exactly as before
   - ✅ No voice fields should appear
   - ✅ Results should only show text message pricing

2. **Voice Only**
   - ✅ Text message fields should be hidden
   - ✅ Voice fields should be visible
   - ✅ Results should show only voice pricing
   - ✅ Test with different voice configurations

3. **Text + Voice**
   - ✅ Both text and voice fields should be visible
   - ✅ Voice AI platform fee should be 0 if text AI is selected
   - ✅ Results should show combined pricing
   - ✅ Total should include both text and voice costs

4. **Edge Cases**
   - ✅ Empty volumes/zero values
   - ✅ Very high volumes (testing tier calculations)
   - ✅ All voice features enabled
   - ✅ Minimal voice features

## Implementation Order

1. **Step 1**: Add configuration to `pricing_config.py`
2. **Step 2**: Add calculation functions to `calculator.py`
3. **Step 3**: Update HTML template (volumes form + results)
4. **Step 4**: Update `app.py` handlers
5. **Step 5**: Test all three channel types
6. **Step 6**: Fix any bugs and refine UI

## Notes

- Currently, voice pricing is only configured for India. Other countries can be added later by extending the configuration dictionaries.
- The voice platform fee discount (0 if text AI is selected) is handled by checking if text AI volume > 0.
- WhatsApp voice tier calculation is based on total minutes (outbound + inbound) to determine the tier, then applies the appropriate rate to each direction.
- All voice costs are currently in INR. Currency conversion can be added later for other countries.

## Analytics integration updates

### Goals
- Track voice channel inputs and computed pricing in the same way text pricing is tracked today.
- Make analytics work for Text Only, Voice Only, and Text + Voice flows.
- Preserve backward compatibility for existing analytics dashboards and CSV exports.

### Schema (DB + Alembic)
- Add columns to the `analytics` table (see `migrations/versions` and SQLAlchemy model usages in `app.py`).
  - `channel_type` (TEXT)
  - Voice config inputs:
    - `voice_ai_enabled` (BOOLEAN/TEXT)
    - `num_voice_journeys` (INTEGER)
    - `num_voice_apis` (INTEGER)
    - `num_additional_voice_languages` (INTEGER)
    - `agent_handover_pstn` (TEXT)
    - `whatsapp_voice_platform` (TEXT)
    - `virtual_number_required` (BOOLEAN/TEXT)
  - Voice volumes and commitments:
    - `pstn_inbound_ai_minutes`, `pstn_inbound_committed` (NUMERIC)
    - `pstn_outbound_ai_minutes`, `pstn_outbound_committed` (NUMERIC)
    - `pstn_manual_minutes`, `pstn_manual_committed` (NUMERIC)
    - `whatsapp_voice_outbound_minutes`, `whatsapp_voice_inbound_minutes` (NUMERIC)
  - Voice pricing outputs:
    - `voice_mandays` (NUMERIC)
    - `voice_dev_cost` (NUMERIC)
    - `voice_platform_fee` (NUMERIC)
    - `whatsapp_setup_fee` (NUMERIC)
    - `voice_cost_pstn_inbound`, `voice_cost_pstn_outbound`, `voice_cost_pstn_manual` (NUMERIC)
    - `voice_cost_wa_outbound`, `voice_cost_wa_inbound` (NUMERIC)
    - `total_voice_cost` (NUMERIC)
  - Summary/derived:
    - `text_total_revenue` (NUMERIC)
    - `voice_total_revenue` (NUMERIC)  // if revenue != cost, otherwise 0
    - `combined_total_invoice` (NUMERIC)
    - `combined_margin_pct` (NUMERIC) // if we implement combined margin

Steps:
- Create an Alembic migration adding the above columns with sensible defaults (NULLable to preserve existing rows).
- Update the write-path where analytics rows are created in `app.py` results step to include voice fields when present.

### CSV/Reporting
- Update `scripts/export_to_csv.py` to export the new columns.
- Update `templates/analytics.html` and any notebooks (e.g., `notebooks/analytics_reports.ipynb`) to include voice segments and breakdowns.
- Add basic cohort/aggregation examples: adoption of voice, average voice minutes per deal, share of voice in combined invoice, etc.

### Logging and observability
- Add explicit debug logs around `channel_type`, presence of `voice_pricing`, and computed totals for faster triage.

## Multi-country support for voice

### Configuration strategy
- Generalize config structures added in Step 1 to accept data for all regions.
  - `PSTN_CALLING_CHARGES` → either per-country dicts or defaults with country overrides.
  - `WHATSAPP_VOICE_CHARGES` → already country-keyed; add `MENA`, `LATAM`, `Africa`, `Europe`, `APAC` tiers when rates are available.
  - Keep India as implemented; for other countries:
    - Interim: fallback to the highest (or explicitly configured) tier until official rates are confirmed.
    - Currency: reuse `COUNTRY_CURRENCY` for display; if voice inputs are in USD regions, store/display in USD.

### Calculation rules
- PSTN: treat as pass-through (no margin) unless cost+markup details are available per country.
- WhatsApp voice:
  - If we obtain Meta cost per region (like the India meta column), compute: revenue = tier_price × minutes, cost = meta_rate × minutes, margin from delta.
  - If no meta provided for a region, treat tier price as a pass-through until rates arrive.

### UI/UX behavior
- The new voice inputs remain the same across countries; tier selection and currency formatting adapt per country selection.
- If a region lacks configured tiers, show a tooltip “Using default/fallback voice rates. Update pricing_config to enable regional tiers.”

### Roadmap staging
- Phase 1: India fully supported; others fallback to defaults with correct currency display.
- Phase 2: Add regional `WHATSAPP_VOICE_CHARGES` and (if available) PSTN specifics; enable margin for voice in those regions.

## Final results page upgrades

### Structure
- Add a dedicated “Voice Channel Pricing” card (as described above) under the current pricing table.
- Add a “Totals” card that summarizes:
  - Text subtotal (existing revenue)
  - Voice subtotal (`total_voice_cost` or voice revenue)
  - Platform fee (text platform fee already included; voice platform fee is inside voice subtotal)
  - Combined Total Invoice
  - Margin presentation options:
    - Option A (quick): show Text Margin only (status quo), label clearly.
    - Option B (enhanced): compute Combined Margin including voice (requires adding voice cost/revenue into `calculate_pricing`).

### Presentation details
- Currency: use `COUNTRY_CURRENCY[country]` consistently across text and voice blocks.
- Formatting: align numbers right; add `smart_format` helper to voice totals for readability (reuse existing Jinja filter).
- Optional toggles:
  - “Include voice in margin” checkbox (internal view only) → controls whether combined margin is shown.
  - Export to CSV/PDF: reuse existing export script; include voice columns when present.

### Data shown per line item
- Voice Development (mandays × rate) and WhatsApp setup (if any)
- Voice Platform Fee
- PSTN: inbound/outbound/manual rows
- WhatsApp Voice: outbound/inbound rows
- Voice Subtotal
- Clear note if any regional fallback rates are applied.

### Error handling & validation
- If `channel_type == 'voice_only'` and text inputs are empty, ensure the flow does not block on required text price fields.
- If required tier data for a country is missing, display a gentle warning and use fallback rate.


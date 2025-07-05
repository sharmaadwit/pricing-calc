# Flask Pricing Calculator App

## Overview
This is a robust, production-ready pricing calculator web application built with Flask. It is designed for messaging services with complex pricing logic, dynamic inclusions, advanced analytics, and a professional UI. The app is suitable for deployment on platforms like Railway.

## Features
- **Dynamic Inclusions:** Shows only the highest/most specific inclusions based on user selections (tiers, add-ons, etc.), avoiding duplicates or contradictions.
- **Detailed Pricing & Margin Tables:** Cleanly formatted, always accurate, and includes both chosen and rate card prices.
- **Discount Validation:** Prevents users from entering prices below allowed thresholds (see table below).
- **Session & Error Handling:** Robust handling of session data and user errors.
- **Professional UI:** Modern, clear, and user-friendly interface.
- **Analytics Dashboard:** Tracks calculations, message volumes, platform fee stats, margins, and more, with both tables and Chart.js graphs.
- **Code Documentation:** Well-commented code and templates for easy maintenance.

## Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd pricing-calc
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app:**
   ```bash
   python app.py
   ```
   Or use your preferred WSGI server (e.g., gunicorn) for production.

## Usage
- Go to the home page and enter your message volumes and platform options.
- Enter your chosen prices (within allowed discount limits).
- View the detailed pricing, inclusions, and margin tables.
- Access the analytics dashboard (with the secret keyword) to view usage stats and trends.
- To reset analytics, send a POST request to `/reset-analytics`.

## Analytics Dashboard
- View total calculations, breakdowns by day/week/country, platform fee stats, message volume distributions, and more.
- For each country, see a table of Average, Min, Max, and Median for platform fee and each message type, plus interactive graphs.

## Code Structure
- `app.py` — Main Flask app, routes, logic, analytics, and inclusions.
- `calculator.py` — Pricing and margin calculation logic.
- `templates/` — HTML templates for the UI and analytics dashboard.
- `static/` — Static files (e.g., diagrams).
- `requirements.txt` — Python dependencies.

## Security
- Analytics dashboard is protected by a secret keyword.
- All user input is validated and sanitized.

## Contributing
Pull requests and suggestions are welcome! Please ensure code is well-documented and tested.

## License
MIT License (or specify your license here)

## Platform Fee and Message Type Pricing Structure

### Platform Fee (Base by Country)
| Country/Region         | Minimum Platform Fee |
|------------------------|---------------------|
| India                  | ₹100,000            |
| Africa, Rest of World  | $500                |
| MENA, LATAM, Europe    | $1,000              |

**Additions for each option (examples):**
- **BFSI Tier 1:** +₹250,000 (India), +$500 (Africa), +$1,500 (others)
- **Personalize Load Standard:** +₹50,000 (India), +$250 (Africa), +$500 (others)
- **Human Agents 20+:** +₹50,000 (India), +$250 (Africa), +$1,000 (LATAM/Europe), +$500 (others)
- ...and so on for other options.

### Message Type Definitions

- **Basic Messages:** Triggered messages via API, Bulk Upload (GS Media, Campaign Manager)

- **Advanced Messages:**
  - Bot platform usage: 2-way messages (JB/Solutions), Triggered messages, Interactive journeys
  - Marketing: Triggered campaigns, Segmented Campaign on Personalize
  - Agent: Agent Interactions, Triggered messages
  - CTX: Retargeting messages
  - Service messages (incoming won't be counted)

- **AI Messages:** Any message that uses AI for responding to the customer

### Message Type Prices (Rate Card Tiers)

#### India
| Message Type         | Volume Tiers (per month)         | Gupshup Fee (INR) |
|----------------------|----------------------------------|-------------------|
| AI                   | 0-10k / 10k-100k / 100k-500k / 500k-1M / 1M+ | 1.00 / 0.90 / 0.80 / 0.70 / 0.60 |
| Advanced             | 0-50k / 50k-150k / 150k-500k / 500k+ | 0.50 / 0.45 / 0.40 / 0.35 |
| Basic Marketing      | All volumes                      | 0.05        |
| Basic Utility        | All volumes                      | 0.03        |

#### MENA
| Message Type         | Volume Tiers (per month)         | Gupshup Fee (USD) |
|----------------------|----------------------------------|-------------------|
| AI                   | 0-10k / 10k-100k / 100k-500k / 500k-1M / 1M+ | 0.084 / 0.076 / 0.067 / 0.059 / 0.050 |
| Advanced             | 0-50k / 50k-150k / 150k-500k / 500k+ | 0.042 / 0.038 / 0.034 / 0.029 |
| Basic Marketing      | All volumes                      | 0.0042      |
| Basic Utility        | All volumes                      | 0.003       |

#### LATAM
| Message Type         | Volume Tiers (per month)         | Gupshup Fee (USD) |
|----------------------|----------------------------------|-------------------|
| AI                   | 0-10k / 10k-100k / 100k-500k / 500k-1M / 1M+ | 0.120 / 0.108 / 0.096 / 0.084 / 0.072 |
| Advanced             | 0-50k / 50k-150k / 150k-500k / 500k+ | 0.060 / 0.054 / 0.048 / 0.042 |
| Basic Marketing      | All volumes                      | 0.006       |
| Basic Utility        | All volumes                      | 0.004       |

#### Africa
| Message Type         | Volume Tiers (per month)         | Gupshup Fee (USD) |
|----------------------|----------------------------------|-------------------|
| AI                   | 0-10k / 10k-100k / 100k-500k / 500k-1M / 1M+ | 0.048 / 0.043 / 0.038 / 0.034 / 0.029 |
| Advanced             | 0-50k / 50k-150k / 150k-500k / 500k+ | 0.024 / 0.022 / 0.019 / 0.017 |
| Basic Marketing      | All volumes                      | 0.002       |
| Basic Utility        | All volumes                      | 0.001       |

#### Europe
| Message Type         | Volume Tiers (per month)         | Gupshup Fee (USD) |
|----------------------|----------------------------------|-------------------|
| AI                   | 0-10k / 10k-100k / 100k-500k / 500k-1M / 1M+ | 0.240 / 0.216 / 0.192 / 0.168 / 0.144 |
| Advanced             | 0-50k / 50k-150k / 150k-500k / 500k+ | 0.120 / 0.108 / 0.096 / 0.084 |
| Basic Marketing      | All volumes                      | 0.012       |
| Basic Utility        | All volumes                      | 0.007       |

#### Rest of the World
| Message Type         | Volume Tiers (per month)         | Gupshup Fee (USD) |
|----------------------|----------------------------------|-------------------|
| AI                   | 0-10k / 10k-100k / 100k-500k / 500k-1M / 1M+ | 0.120 / 0.108 / 0.096 / 0.084 / 0.072 |
| Advanced             | 0-50k / 50k-150k / 150k-500k / 500k+ | 0.060 / 0.054 / 0.048 / 0.042 |
| Basic Marketing      | All volumes                      | 0.006       |
| Basic Utility        | All volumes                      | 0.007       |

--- 
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
   cd pythonProject
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

## Discount Rules
The following table summarizes the maximum discounts users can give for each item:

| Item                              | Maximum Discount Allowed | Minimum Price (as % of Rate Card) |
|------------------------------------|-------------------------|------------------------------------|
| **AI Message**                    | 70%                     | 30%                                |
| **Advanced Message**               | 70%                     | 30%                                |
| **Basic Utility/Authentication**   | 70%                     | 30%                                |
| **Basic Marketing Message**        | 90%                     | 10%                                |
| **Platform Fee**                   | 70%                     | 30%                                |

*If a user tries to enter a price lower than the minimum allowed, the app will show an error and block the calculation.*

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
# AB Testing Tool

A statistics-powered API that helps product managers and growth teams run better experiments.

Built with FastAPI and Python. No more gut-feel decisions or stopping tests too early.

## What it does

- **/analyze** — takes raw experiment data and returns statistical significance, p-value, uplift, and confidence intervals
- **/sample-size** — calculates how many visitors you need before starting a test
- **/interpret** — cross-references your results against required sample size and returns a plain English recommendation with risk assessment

## The problem it solves

Most PMs either call tests too early or do not know how much data they need before starting. This tool catches both mistakes and explains the reasoning in plain English that any stakeholder can understand.

## How to run locally

1. Clone the repo
2. Create a virtual environment: python -m venv venv
3. Activate it: venv\Scripts\activate (Windows) or source venv/bin/activate (Mac)
4. Install dependencies: pip install -r requirements.txt
5. Start the server: uvicorn main:app --reload
6. Open http://127.0.0.1:8000/docs for the interactive API explorer

## Example: catching a common PM mistake

A PM runs a test for 3 days, sees a 40% uplift and wants to ship.

Request to /interpret:
- control: 500 visitors, 25 conversions
- variant: 500 visitors, 35 conversions

Response:
- recommendation: Keep running
- reasoning: The test has not reached the required 8155 visitors per group yet. It is too early to make any decision.
- risk: High - stopping early is the most common mistake in experimentation.

## Tech stack

- FastAPI - API framework
- statsmodels - statistical tests
- scipy - Z-score calculations
- uvicorn - ASGI server

## Roadmap

- [ ] Phase 2: Framer front-end with interactive visualisations
- [ ] Phase 3: Experiment tracker with Supabase
- [ ] Phase 4: Notion and Google Sheets export

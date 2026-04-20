# AB Testing Tool

A statistics-powered tool that helps product managers and growth teams run better experiments.

Live at: https://abtestingtool.framer.website

Built with FastAPI, Python, and Framer. No more gut-feel decisions or stopping tests too early.

## What it does

- **Analyze results** — enter experiment data and get statistical significance, p-value, uplift, and a confidence interval visualisation
- **Sample size calculator** — find out how many visitors you need before starting a test
- **Interpret endpoint** — cross-references results against required sample size and returns a plain English recommendation with risk assessment

## The problem it solves

Most PMs either call tests too early or do not know how much data they need before starting. This tool catches both mistakes and explains the reasoning in plain English that any stakeholder can understand.

## How to run locally

1. Clone the repo
2. Create a virtual environment: python -m venv venv
3. Activate it: venv\Scripts\activate (Windows) or source venv/bin/activate (Mac)
4. Install dependencies: pip install -r requirements.txt
5. Start the server: uvicorn main:app --reload
6. Open http://127.0.0.1:8000/docs for the interactive API explorer

## Tech stack

- FastAPI - API framework
- statsmodels - statistical tests
- scipy - Z-score calculations
- uvicorn - ASGI server
- Framer - frontend
- Railway - backend deployment

## Roadmap

- [x] Phase 1: Statistical API with analyze, sample-size, and interpret endpoints
- [x] Phase 2: Framer frontend with confidence interval visualisation
- [ ] Phase 3: Experiment tracker with Supabase
- [ ] Phase 4: Notion and Google Sheets export

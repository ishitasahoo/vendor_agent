# VendorFind — Layer 1: User Interface

A Streamlit app that is the front door of your wellness vendor sourcing agent.

## Setup (one time)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

The app opens automatically in your browser at http://localhost:8501

## What this file is

`app.py` is Layer 1 only. It contains:
- The UI layout (mode toggle, search inputs, results table, run history)
- A `run_agent()` stub function that currently returns dummy data

## How to connect Layer 2

Replace the body of `run_agent()` in app.py with your real Claude API agent call.
The function receives:
  - `mode`       — "events" or "stores"
  - `goal`       — free-text description of what to find
  - `location`   — location string from the user
  - `date_range` — tuple of (from, to) strings, events mode only

It must return a list of dicts. Each dict is one row in the results table.

Events schema:
  Event name, Date, Type, Booth cost ($), Deadline, Location, Contact, Website, Notes

Stores schema:
  Store name, Address, Type, Sub-type, Phone, Website, Notes

## Files

- app.py           — the entire Layer 1 UI
- requirements.txt — pip dependencies

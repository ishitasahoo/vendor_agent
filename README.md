# VendorFind — AI-Powered Vendor Sourcing Platform

VendorFind is an AI-powered application designed to automate the process of discovering vendor booth opportunities and retail store leads. The platform uses an agent-based workflow to help users efficiently research and identify potential business opportunities.

## Overview

VendorFind allows users to search for:

- Vendor events and booth opportunities
- Retail stores and potential business leads

The application is built as a multi-layer AI system, with the Streamlit interface serving as the entry point for interacting with the sourcing agent.

## Current Features

### Layer 1: User Interface

The Streamlit frontend includes:

- Search mode selection (Events or Stores)
- User input fields for sourcing goals and locations
- Event date range filtering
- Results table display
- Run history tracking

## Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
streamlit run app.py
```

The app will open automatically in your browser at:

```
http://localhost:8501
```

## Architecture

VendorFind is designed as a multi-layer agentic application:

### Layer 1 — User Interface
- Built with Streamlit
- Handles user inputs and displays sourcing results

### Layer 2 — AI Agent Workflow
- Processes sourcing requests
- Uses Claude API for intelligent research and automation

### Layer 3 — Data Integration
- Connects with external data sources
- Stores and organizes results through integrations such as Google Sheets

## Input Parameters

The `run_agent()` function receives:

- `mode` — `"events"` or `"stores"`
- `goal` — User's sourcing objective
- `location` — Target location
- `date_range` — Event date range (events mode only)

## Output Format

The agent returns structured results as a list of dictionaries.

### Events

Results include:

- Event name
- Date
- Type
- Booth cost ($)
- Deadline
- Location
- Contact
- Website
- Notes

### Stores

Results include:

- Store name
- Address
- Type
- Sub-type
- Phone
- Website
- Notes

## Files

| File | Description |
|------|-------------|
| `app.py` | Streamlit user interface |
| `requirements.txt` | Python dependencies |

## Technologies Used

- Python
- Streamlit
- Anthropic Claude API
- Google Sheets API
- Git/GitHub

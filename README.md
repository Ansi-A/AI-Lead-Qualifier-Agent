# AI Lead Qualifier Agent

> **Status: In Progress — 70% Complete**

Automated lead qualification system using LLM-powered reasoning to screen and score prospects from email sources.

---

## What It Does

- Connects to IMAP email inbox (Gmail, Outlook, etc.)
- Fetches and parses incoming lead emails
- Uses LLM API to analyze email content
- Returns qualification score + reasoning for each lead
- Stores results in PostgreSQL database

---

## Tech Stack

| Category | Tools |
|----------|-------|
| Backend | Python, FastAPI |
| Database | PostgreSQL, SQLAlchemy |
| Email | IMAP, `imaplib` |
| AI | LLM API (OpenAI/Anthropic compatible) |
| Auth | JWT, bcrypt |

---

## Current Status (70% Complete)

### Done
- IMAP email fetching and parsing
- LLM integration with function calling
- Database models and schemas (SQLAlchemy + Pydantic)
- Lead qualification logic
- Config management with `.env`
- Basic error handling

### In Progress
- FastAPI endpoints for manual lead submission
- Authentication system (JWT)
- Lead history and tracking

### Left to Do
- Full test suite (unit + integration)
- Docker containerization
- CI/CD pipeline (GitHub Actions)
- Production deployment (Render / Railway / AWS)
- Webhook support for external integrations
- Admin dashboard (basic UI)

---

## Project Structure

___STILL IN PROGRESS SO WILL KEEP CHANGING ___
___fINAL IN MODULAR STRUCTURE SO______
___STILL IN TESTING_________


---
## Environment Variables Required .env

DATABASE_URL=postgresql://user:pass@localhost/dbname
IMAP_SERVER=imap.gmail.com
IMAP_EMAIL=your-email@gmail.com
IMAP_PASSWORD=your-app-password
LLM_API_KEY=your-api-key
SECRET_KEY=your-secret-key

## PostgreSQL Installation & Setup

### Ubuntu / Debian (Pop-OS)

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Check status (should be active)
sudo systemctl status postgresql

# Start if not running
sudo systemctl start postgresql
sudo systemctl enable postgresql

## Quick Start (Local)
create db leadgate

________________________________________________________________
# Clone
git clone https://github.com/Ansi-A/AI-Lead-Qualifier-Agent.git
cd AI-Lead-Qualifier-Agent

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Set up .env (copy and fill)
cp .env.example .env

# Run (once FastAPI endpoints are ready)
uvicorn main:app --reload

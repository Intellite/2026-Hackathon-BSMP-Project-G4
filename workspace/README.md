# Compass AI (Hackathon Prototype)

AI-powered student success platform.

## Features
- Auth (signup/login/logout)
- Student dashboard with career match + scholarships + skill gap summary
- Career explorer (AI-generated recommendations)
- Career roadmap generator (timeline)
- Opportunity gap detector (progress bars)
- Scholarship finder (filtering)
- AI mentor chat (conversation history stored in SQLite)
- Resume analyzer (upload + AI analysis)
- Future earnings simulator (chart placeholders)
- Profile center + settings

## Tech Stack
- Python 3.12
- Flask + Blueprint architecture
- Jinja2 templates
- Bootstrap 5 + Vanilla JS
- SQLite + SQLAlchemy ORM
- Flask-Login
- AI via OpenAI-compatible endpoints (provider abstraction)

## Setup
1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Copy env:
   - `cp .env.example .env`
4. (Optional) Set `AI_API_KEY` and `AI_BASE_URL` in `.env`.
5. Run:
   - `python run.py`

## .env configuration
See `.env.example`.

Key variables:
- `SECRET_KEY`
- `DATABASE_URL` (default: `sqlite:///compass_ai.sqlite3`)
- `AI_BASE_URL` (OpenAI-compatible)
- `AI_API_KEY`
- `AI_MODEL`
- `AI_RATE_LIMIT_PER_MINUTE`

## API configuration
Compass AI uses an abstraction layer (`app/services/ai_service.py`) that calls an OpenAI-compatible chat completions endpoint.

## Future improvements
- Add real chart rendering (Chart.js) and richer analytics
- Add background jobs for AI calls
- Add admin panel and moderation
- Improve prompt engineering and structured outputs

## Architecture
- `app/__init__.py`: app factory + extensions
- `app/routes/*`: Blueprint routes
- `app/models/*`: SQLAlchemy models
- `app/services/*`: AI service abstraction + prompt files
- `app/templates/*`: Jinja2 templates
- `app/static/*`: CSS/JS/images
- `app/utils/*`: helpers (rate limiting, logging, etc.)

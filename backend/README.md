# Complaint Ticketing System Backend

Backend service for the complaint ticketing system that handles complaint classification, routing, and management using AI.

## Prerequisites

- Python 3.10 or higher
- uv package manager
- SQLite database

## Installation



1. Create a virtual environment using uv
```bash
uv venv
```

2. Install dependencies
```bash
uv sync
```

## Configuration

Create a `.env` file in the backend directory with the following variables:

```env
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=sqlite:///complaints.db
JWT_SECRET_KEY=your-secret-key
```

## Running the Application

1. Initialize the database
```bash
uv run flask db upgrade
```

2. Start the development server
```bash
uv run flask run
```

The server will start at `http://localhost:5000`

## API Routes

- `POST /api/auth/login` - User authentication
- `POST /api/auth/register` - New user registration
- `POST /api/complaints` - Submit new complaint
- `GET /api/complaints` - List all complaints
- `GET /api/complaints/:id` - Get specific complaint
- `PUT /api/complaints/:id` - Update complaint status
- `GET /api/analytics/dashboard` - Get dashboard metrics

## Development

1. Make your changes
2. Run tests
```bash
uv run pytest
```
3. Submit a pull request

## Project Structure

```
backend/
├── app.py              # Main application entry point
├── config.py           # Configuration settings
├── extensions.py       # Flask extensions
├── models/            # Database models
├── services/          # Business logic and services
├── migrations/        # Database migrations
└── static/           # Static files
```

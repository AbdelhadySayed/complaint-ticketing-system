# Complaint Ticketing System

A smart complaint management platform that combines AI classification with human expertise for efficient ticket resolution. The system automatically categorizes complaints, generates initial responses, and routes tickets to appropriate customer service representatives.

---

## Features

- Automated complaint classification using machine learning
- AI-generated initial responses
- Smart routing to customer service teams
- Real-time complaint tracking and monitoring
- Analytics dashboard for performance metrics
- Dual response system (AI + Human)

---

## Technology Stack

### Frontend
- React.js
- Tailwind CSS
- TypeScript

### Backend
- Flask (Python)
- SQLAlchemy
- JWT Authentication
- REST API

### AI Components
- Scikit-learn for classification
- Natural Language Processing for response generation
- ChromaDB for vector storage

---

## Installation and Setup

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
uv venv


# Install dependencies
uv sync


# Initialize database
uv run flask db upgrade

# Run the server
uv run flask run
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install


# Start development server
npm run dev
```

---

## API Documentation

### Authentication
- POST /api/auth/login - User authentication
- POST /api/auth/register - New user registration

### Complaints
- POST /api/complaints - Submit new complaint
- GET /api/complaints - List all complaints
- GET /api/complaints/:id - Get specific complaint
- PUT /api/complaints/:id - Update complaint status

### Analytics
- GET /api/analytics/dashboard - Get dashboard metrics
- GET /api/analytics/performance - Get team performance data

---

## User Types

### Regular Users
- Submit and track complaints
- View complaint history
- Rate responses
- Download complaint records

### Customer Service Representatives
- View assigned complaints
- Review AI suggestions
- Respond to tickets
- Update ticket status

### Administrators
- Access analytics dashboard
- Manage user accounts
- Configure AI settings
- Generate reports

---

## Environment Variables

### Backend
```
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=sqlite:///complaints.db
JWT_SECRET_KEY=your-secret-key
AI_MODEL_PATH=./models
```

### Frontend
```
VITE_API_URL=http://localhost:5000
VITE_ENV=development
```

---

## Development

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

---

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## License

MIT License - See LICENSE file for details.

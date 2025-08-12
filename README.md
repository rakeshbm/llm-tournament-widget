# LLM Prompt Arena

A web application that helps you discover the most effective prompts through head-to-head competition. Test multiple prompt variations against the same question and let voting determine the winner in a tournament-style bracket.

## Features

- **Tournament Creation**: Set up competitions with 2-8 different prompts
- **Bracket System**: Automatic tournament bracket generation with proper bye handling
- **Head-to-Head Voting**: Compare prompt responses side-by-side
- **Tournament History**: View and continue past tournaments
- **Progress Tracking**: Visual progress bars and completion status (user-specific)
- **LLM Integration**: Automatic response generation using OpenRouter API

## Tech Stack

**Frontend:**
- React (Vite)
- TypeScript
- Styled Components
- Docker + Nginx

**Backend:**
- Python 3.12
- Flask
- SQLAlchemy
- PostGreSQL
- OpenRouter API Integration

## Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenRouter API key

### Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/rakeshbm/llm-tournament-widget.git
cd llm-tournament-widget
```

2. Set up environment variables:
```python
# Create a .env file in the project's root directory
POSTGRES_USER=your_db_user
POSTGRES_DB=your_db_name
POSTGRES_PASSWORD=your_db_password
```

```python
# Create a .env file in the "backend" directory
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

```python
# Create a .env file in the "frontend" directory
VITE_API_BASE=your_backend_url
```

### Running the Application

Start both frontend and backend services:

```bash
docker-compose up --build
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

To run in detached mode:
```bash
docker-compose up -d --build
```

To stop the services:
```bash
docker-compose down
```

## Usage

1. **Create a Tournament**:
   - Enter a question that all prompts should answer
   - Add 2-8 different prompt variations
   - Click "Submit"

2. **Vote on Matches**:
   - Compare responses side-by-side
   - Click on the better response to advance it
   - Continue until a winner is determined

3. **View Results**:
   - See the tournament bracket progression
   - View the winning prompt and completion status
   - Access tournament history for past competitions

## API Endpoints

### Tournaments
- `POST /tournaments` - Create new tournament
- `GET /tournaments` - List all tournaments
- `GET /tournaments/{id}` - Get specific tournament with user state
- `POST /tournaments/{id}/vote` - Submit vote for match
- `GET /tournaments/{id}/results` - Get aggregated tournament results

### Project Structure
```
├── backend/
│   ├── app/
|   |   |__ core/              # Core setup
│   │   ├── models.py          # Database models
│   │   ├── routes/            # API routes
│   │   ├── services/          # Business logic
│   │   └── utils.py           # Utility functions
|   |   |__ config.py          # App config            
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
|   |   |__ App.tsx
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom hooks
│   │   ├── types/             # TypeScript types
│   │   └── styles/            # Styled components
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## Configuration


### LLM Model

The application uses `mistralai/mistral-7b-instruct` by default. You can modify the model in `backend/app/utils.py`:

```python
LLM_MODEL = "mistralai/mistral-7b-instruct"  # Change this line
```

## Running Tests

```bash
docker compose -f docker-compose.test.yml up --abort-on-container-exit --build
```

## Troubleshooting

**Common Issues:**

1. **Port conflicts**: Change ports in `docker-compose.yml` if 3000 or 5000 are in use
2. **API key errors**: Ensure `OPENROUTER_API_KEY` is set correctly
3. **Database issues**: Ensure `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` are set correctly

**Logs:**
```bash
# View logs for all services
docker-compose logs

# View logs for specific service
docker-compose logs backend
docker-compose logs frontend
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request

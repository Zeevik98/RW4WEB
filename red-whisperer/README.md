# Red-Whisperer Multi-Agent Orchestrator

An advanced autonomous red-teaming orchestrator that leverages GPT-4 for intelligent security testing automation.

## Features

- Multi-agent architecture for different types of security testing
- GPT-4 powered payload generation and analysis
- Secure, immutable logging system
- REST-based communication between components
- Comprehensive BDD testing suite

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- OpenAI API key

## Project Structure

```
red-whisperer/
├── orchestrator/         # Orchestrator service
├── agents/              # Individual agent implementations
│   ├── sql_injection/
│   ├── xss/
│   └── phishing/
├── tests/               # BDD test suite
├── logs/                # Immutable log storage
└── docker/              # Docker configuration
```

## Setup and Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd red-whisperer
```

2. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your-api-key-here
```

3. Build and start the containers:
```bash
docker-compose up --build
```

## Running Tests

To run the BDD test suite:

```bash
docker-compose run --rm test pytest tests/
```

## Usage

1. Start the system:
```bash
docker-compose up -d
```

2. Create a new task:
```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "unique-task-id",
    "task_type": "sql_injection",
    "target": "http://target.com",
    "parameters": {
      "method": "POST",
      "parameters": ["username", "password"]
    }
  }'
```

3. Monitor task status:
```bash
curl http://localhost:8000/tasks/{task_id}
```

## Security Considerations

- All logs are stored in an immutable volume
- API keys are managed through environment variables
- Communication between components is secured
- Each agent runs in its own container with limited permissions

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for GPT-4 integration
- FastAPI for the REST API framework
- Docker for containerization 
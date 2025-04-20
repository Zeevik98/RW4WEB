# Red-Whisperer Security Testing Framework

A2A-compliant security testing framework for web applications.

## Features

- XSS and SQL Injection testing
- A2A compliance
- AI-powered vulnerability analysis
- Automated test orchestration
- Comprehensive reporting

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Zeevik98/RW4WEB.git
cd RW4WEB
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```bash
cp .env.example .env
```

5. Update the `.env` file with your API keys:
```bash
OPENAI_API_KEY=your_api_key_here
A2A_AUTH_TOKEN=your_auth_token_here
```

## Usage

1. Start the orchestrator:
```bash
python -m orchestrator.main
```

2. Run tests:
```bash
python -m pytest tests/
```

## A2A Compliance

This framework implements the following A2A compliance features:

- Agent discovery
- Health check endpoints
- Authentication and authorization
- Version compatibility checks
- Heartbeat monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Security
Please report any security issues to security@example.com

## Acknowledgments
- Google A2A Ecosystem
- OpenAI
- Security Research Community 
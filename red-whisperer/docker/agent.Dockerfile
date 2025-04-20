# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agents/ /app/agents/
COPY orchestrator/ /app/orchestrator/

# Create log directory with appropriate permissions
RUN mkdir -p /var/log/red-whisperer && \
    chmod 755 /var/log/red-whisperer

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the agent
CMD ["python", "-m", "agents.${AGENT_TYPE}.agent"] 
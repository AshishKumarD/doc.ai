# Dockerfile for Jira RAG Documentation Assistant
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements/base.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY src/ /app/src/
COPY scripts/ /app/scripts/
COPY config/ /app/config/

# Create directories for data
RUN mkdir -p /app/data/chroma_db /app/data/documentation

# Expose port for Gradio web interface
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden)
CMD ["python", "src/cli/2_query_cli.py"]

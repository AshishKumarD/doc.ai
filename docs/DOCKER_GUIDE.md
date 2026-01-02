# JiraDocAI - Docker Setup Guide

Complete guide to running JiraDocAI in Docker containers - isolated from your main system.

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)
- Claude API key from [Anthropic Console](https://console.anthropic.com/)

## Quick Start (3 Steps)

### 1. Set Your API Key

Create a `.env` file in the `jiradocai` directory:

```bash
cd /Users/ashish/Jira/jiradocai
echo "ANTHROPIC_API_KEY=your-actual-api-key-here" > .env
```

Or export it in your shell:

```bash
export ANTHROPIC_API_KEY='your-actual-api-key-here'
```

### 2. Build the Docker Image

```bash
docker-compose build
```

This will:
- Create a Python 3.11 environment
- Install all dependencies (LlamaIndex, ChromaDB, etc.)
- Set up the application

### 3. Run JiraDocAI

Choose your preferred method:

#### Option A: Interactive Container (Recommended for First Time)

```bash
# Start the container
docker-compose up -d jiradocai

# Access the container shell
docker exec -it jiradocai-assistant bash

# Inside container - Index your documents (first time only)
python 1_index_documents.py

# Inside container - Query via CLI
python 2_query_cli.py
```

#### Option B: Web Interface (Easiest)

```bash
# Start the web UI service
docker-compose --profile web up jiradocai-web
```

Then open: http://localhost:7860

## Architecture

### Container Structure

```
┌─────────────────────────────────────┐
│   JiraDocAI Container               │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Python 3.11                 │  │
│  │  - LlamaIndex               │  │
│  │  - ChromaDB                 │  │
│  │  - HuggingFace Embeddings  │  │
│  │  - Claude API Client       │  │
│  └──────────────────────────────┘  │
│                                     │
│  Volumes (Mounted):                 │
│  - /app/docs → Your Jira docs      │
│  - /app/chroma_jira_db → Vector DB │
│                                     │
│  Exposed Ports:                     │
│  - 7860 → Gradio Web UI            │
└─────────────────────────────────────┘
```

### Volume Mounts

1. **Documentation** (`/Users/ashish/Jira/Issue1` → `/app/docs`)
   - Read-only mount of your Jira documentation
   - Container accesses your docs without copying

2. **Vector Database** (`./chroma_jira_db` → `/app/chroma_jira_db`)
   - Persists the indexed data
   - Survives container restarts
   - Shareable between containers

3. **Scripts** (Development only)
   - Python scripts mounted for live editing
   - Changes reflected immediately

## Complete Usage Guide

### First Time Setup

1. **Build and start container**:
```bash
docker-compose up -d jiradocai
```

2. **Index your documentation** (one-time):
```bash
docker exec -it jiradocai-assistant python 1_index_documents.py
```

This creates the vector database. Takes 5-10 minutes depending on doc size.

3. **Query your docs**:

**CLI Method**:
```bash
docker exec -it jiradocai-assistant python 2_query_cli.py
```

**Web UI Method**:
```bash
docker-compose --profile web up jiradocai-web
# Open http://localhost:7860
```

### Subsequent Usage

Once indexed, you can query anytime:

```bash
# Start container if not running
docker-compose up -d jiradocai

# Query directly
docker exec -it jiradocai-assistant python 2_query_cli.py

# Or use web UI
docker-compose --profile web up jiradocai-web
```

## Docker Commands Reference

### Container Management

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d jiradocai

# Stop all services
docker-compose down

# Stop but keep data
docker-compose stop

# Restart service
docker-compose restart jiradocai

# View logs
docker-compose logs -f jiradocai

# Check status
docker-compose ps
```

### Interactive Shell

```bash
# Access container shell
docker exec -it jiradocai-assistant bash

# Run Python script
docker exec -it jiradocai-assistant python 2_query_cli.py

# Run one-off command
docker exec jiradocai-assistant python -c "print('Hello')"
```

### Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove containers and volumes (deletes index!)
docker-compose down -v

# Remove Docker image
docker rmi jiradocai-jiradocai

# Clean up everything (careful!)
docker-compose down -v --rmi all
```

### Rebuild After Changes

```bash
# Rebuild after code changes
docker-compose build

# Force rebuild (no cache)
docker-compose build --no-cache

# Rebuild and restart
docker-compose up -d --build
```

## Advanced Configurations

### Custom Document Path

Edit `docker-compose.yml`:

```yaml
volumes:
  - /your/custom/path:/app/docs:ro  # Change this line
```

### Different Port for Web UI

Edit `docker-compose.yml`:

```yaml
ports:
  - "8080:7860"  # Host:Container (change 8080 to your preference)
```

### Use More CPU/Memory

Add resource limits in `docker-compose.yml`:

```yaml
services:
  jiradocai:
    ...
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
```

### Enable GPU (for faster embeddings)

Requires NVIDIA Docker runtime:

```yaml
services:
  jiradocai:
    ...
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

Update embedding code to use GPU:
```python
embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5",
    device="cuda"
)
```

### Multiple Documentation Sets

Create multiple services in `docker-compose.yml`:

```yaml
services:
  jiradocai-prod:
    build: .
    container_name: jiradocai-prod
    volumes:
      - /path/to/prod/docs:/app/docs:ro
      - ./chroma_prod_db:/app/chroma_jira_db

  jiradocai-test:
    build: .
    container_name: jiradocai-test
    volumes:
      - /path/to/test/docs:/app/docs:ro
      - ./chroma_test_db:/app/chroma_jira_db
    ports:
      - "7861:7860"  # Different port
```

## Environment Variables

Set in `.env` file or `docker-compose.yml`:

```env
# Required
ANTHROPIC_API_KEY=sk-ant-xxx

# Optional
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs jiradocai

# Common issues:
# 1. Port already in use
docker-compose ps  # Check if already running
docker-compose down  # Stop existing containers

# 2. Invalid API key
docker exec -it jiradocai-assistant printenv ANTHROPIC_API_KEY
```

### Can't access web UI

```bash
# Check if service is running
docker-compose ps

# Check if port is exposed
docker port jiradocai-web

# Try accessing
curl http://localhost:7860
```

### Database not persisting

```bash
# Check if volume is mounted
docker inspect jiradocai-assistant | grep Mounts -A 10

# Ensure local directory exists
ls -la ./chroma_jira_db
```

### Out of memory

```bash
# Check container resources
docker stats jiradocai-assistant

# Add memory limits (see Advanced Configurations above)
```

### Slow performance

```bash
# Use smaller embedding model
# Edit Python scripts:
embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"  # Smaller, faster
)

# Reduce number of retrieved documents
query_engine = index.as_query_engine(
    similarity_top_k=2  # Reduce from 3 to 2
)
```

### Permission issues with volumes

```bash
# Fix ownership (Linux/Mac)
sudo chown -R $(whoami) ./chroma_jira_db

# Or run container as your user
docker-compose run --user $(id -u):$(id -g) jiradocai python 2_query_cli.py
```

## Development Workflow

### Editing Code

1. **Mounted volumes** allow live editing:
```bash
# Edit on host
vim /Users/ashish/Jira/jiradocai/2_query_cli.py

# Run updated code immediately
docker exec -it jiradocai-assistant python 2_query_cli.py
```

2. **Rebuild for major changes**:
```bash
docker-compose build
docker-compose up -d
```

### Testing Changes

```bash
# Run tests in container
docker exec -it jiradocai-assistant pytest

# Run specific script
docker exec -it jiradocai-assistant python test_query.py
```

### Debugging

```bash
# Interactive Python shell
docker exec -it jiradocai-assistant python

# Install debugging tools
docker exec -it jiradocai-assistant pip install ipdb
docker exec -it jiradocai-assistant python -m ipdb script.py
```

## Production Deployment

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml jiradocai

# Scale service
docker service scale jiradocai_jiradocai=3
```

### Kubernetes

Convert docker-compose to Kubernetes:

```bash
# Using kompose
brew install kompose
kompose convert -f docker-compose.yml

# Apply to cluster
kubectl apply -f jiradocai-deployment.yaml
```

### Cloud Deployment

**AWS ECS**:
```bash
# Push image to ECR
docker tag jiradocai-jiradocai:latest <account>.dkr.ecr.<region>.amazonaws.com/jiradocai:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/jiradocai:latest

# Create ECS task definition and service
```

**Google Cloud Run**:
```bash
# Build and push
gcloud builds submit --tag gcr.io/<project>/jiradocai

# Deploy
gcloud run deploy jiradocai --image gcr.io/<project>/jiradocai --platform managed
```

## Benefits of Docker Approach

✅ **Isolation**: No conflicts with your system Python
✅ **Reproducible**: Same environment everywhere
✅ **Portable**: Run on any machine with Docker
✅ **Clean**: Easy to remove completely
✅ **Scalable**: Deploy multiple instances
✅ **Version Control**: Track image versions
✅ **Easy Rollback**: Return to previous version

## Comparison: Docker vs Native

| Aspect | Docker | Native |
|--------|--------|--------|
| Setup Time | 5 min | 15 min |
| Isolation | ✅ Complete | ❌ Shared environment |
| Dependencies | Containerized | System-wide |
| Cleanup | `docker-compose down` | Uninstall packages |
| Deployment | `docker push` | Manual setup |
| Scalability | Easy | Difficult |

## Next Steps

1. ✅ **Build**: `docker-compose build`
2. ✅ **Start**: `docker-compose up -d jiradocai`
3. ✅ **Index**: `docker exec -it jiradocai-assistant python 1_index_documents.py`
4. ✅ **Query**: `docker exec -it jiradocai-assistant python 2_query_cli.py`
5. ✅ **Web UI**: `docker-compose --profile web up jiradocai-web`

## Resources

- **Main README**: `README.md`
- **Python Setup Guide**: `FREE_RAG_SETUP.md` (in knowledge folder)
- **Docker Docs**: https://docs.docker.com/
- **Docker Compose Docs**: https://docs.docker.com/compose/

---

**Ready to start!** Run: `docker-compose build`

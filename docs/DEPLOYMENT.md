# JiraDocAI - Deployment Guide

**Make your Xray documentation assistant available to anyone!**

## Deployment Options

### Option 1: Local Network (Easiest - 2 minutes)

**Best for**: Sharing with teammates on same network

```bash
# Edit 3_query_web.py, change this line:
# FROM:
demo.launch(share=False, server_name="127.0.0.1", server_port=7860)

# TO:
demo.launch(share=False, server_name="0.0.0.0", server_port=7860)
```

Then restart:
```bash
lsof -ti:7860 | xargs kill -9 2>/dev/null
source venv/bin/activate && python 3_query_web.py
```

**Access from other computers on your network:**
```
http://YOUR_IP_ADDRESS:7860
```

Find your IP: `ifconfig | grep "inet " | grep -v 127.0.0.1`

---

### Option 2: Public Internet with Gradio Share (5 minutes)

**Best for**: Quick demo, temporary sharing

```bash
# Edit 3_query_web.py, change:
demo.launch(share=True, server_name="127.0.0.1", server_port=7860)
```

Restart and you'll get a **public URL** like:
```
https://xxxxx.gradio.live
```

**Pros**:
- ✅ Instant public access
- ✅ No setup required
- ✅ Free

**Cons**:
- ❌ Link expires after 72 hours
- ❌ Limited to Gradio's infrastructure
- ❌ Slower than dedicated hosting

---

### Option 3: Docker Deployment (Production-Ready)

**Best for**: Reliable, scalable deployment

#### A. Local Docker

```bash
cd /Users/ashish/Jira/jiradocai

# Build image
docker build -t jiradocai:latest .

# Run container
docker run -d \
  --name jiradocai \
  -p 7860:7860 \
  -v /Users/ashish/Jira/xray_documentation:/app/docs:ro \
  -v $(pwd)/chroma_jira_db:/app/chroma_jira_db \
  jiradocai:latest \
  python 3_query_web.py
```

Access at: `http://your-server-ip:7860`

#### B. Docker Compose (Recommended)

Already configured! Just run:

```bash
docker-compose build
docker-compose up -d jiradocai-web
```

---

### Option 4: Cloud Deployment

#### A. **DigitalOcean** (Easiest Cloud Option)

**Cost**: ~$6/month for basic droplet

1. **Create Droplet**
```bash
# Create Ubuntu 22.04 droplet (Basic $6/mo)
# SSH into it
```

2. **Setup**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b

# Clone your project
git clone YOUR_REPO
cd jiradocai

# Build and run
docker-compose up -d
```

3. **Access**
```
http://YOUR_DROPLET_IP:7860
```

#### B. **AWS EC2**

**Cost**: ~$10-30/month depending on instance

1. **Launch Instance**
   - AMI: Ubuntu 22.04
   - Instance type: t3.medium (4GB RAM minimum)
   - Security group: Allow port 7860

2. **Setup** (same as DigitalOcean above)

3. **Optional: Use Elastic IP** for permanent address

#### C. **Google Cloud Run** (Serverless)

**Cost**: Pay per use (~$0.50-5/month for light usage)

```bash
# Build container
docker build -t gcr.io/YOUR_PROJECT/jiradocai .

# Push to Google Container Registry
docker push gcr.io/YOUR_PROJECT/jiradocai

# Deploy
gcloud run deploy jiradocai \
  --image gcr.io/YOUR_PROJECT/jiradocai \
  --platform managed \
  --port 7860 \
  --memory 4Gi \
  --timeout 300s
```

#### D. **Render.com** (Easiest, Free Tier Available)

**Cost**: Free tier available, $7/month for better performance

1. Connect your GitHub repo
2. Create new Web Service
3. Configure:
   - Build: `pip install -r requirements.txt && playwright install chromium`
   - Start: `python 3_query_web.py`
   - Port: 7860

---

### Option 5: Reverse Proxy with Domain Name

**Best for**: Professional deployment with custom domain

#### Using Nginx

```bash
# Install Nginx
sudo apt install nginx

# Create config
sudo nano /etc/nginx/sites-available/jiradocai
```

```nginx
server {
    listen 80;
    server_name xray-docs.yourcompany.com;

    location / {
        proxy_pass http://localhost:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/jiradocai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Add HTTPS with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d xray-docs.yourcompany.com
```

Now accessible at: `https://xray-docs.yourcompany.com`

---

### Option 6: Multi-User Deployment with Authentication

#### Add Basic Auth (Simple)

Create `auth_wrapper.py`:

```python
import gradio as gr
from functools import wraps

# Simple password protection
AUTHORIZED_USERS = {
    "admin": "secure_password",
    "team": "team_password"
}

def check_auth(username, password):
    return AUTHORIZED_USERS.get(username) == password

# Modify 3_query_web.py to use gr.Blocks instead of ChatInterface
# and add authentication
```

#### Add OAuth (Advanced)

Use Nginx with OAuth2 Proxy for enterprise authentication (Google, GitHub, etc.)

---

## Deployment Checklist

### Pre-Deployment

- [ ] Test locally thoroughly
- [ ] Verify all 465 pages indexed
- [ ] Check ChromaDB size (~11MB is normal)
- [ ] Test on different questions
- [ ] Verify sources show URLs correctly

### Security

- [ ] Change from `0.0.0.0` to specific IP if needed
- [ ] Add firewall rules (only allow port 7860)
- [ ] Consider adding authentication
- [ ] Use HTTPS in production
- [ ] Rate limiting for public deployments
- [ ] Regular backups of ChromaDB

### Performance

- [ ] Ensure Ollama is running (`ollama serve` or `brew services start ollama`)
- [ ] Monitor RAM usage (4GB minimum recommended)
- [ ] Consider GPU for faster responses
- [ ] Cache frequent queries if needed

### Monitoring

- [ ] Set up logging
- [ ] Monitor uptime
- [ ] Track query patterns
- [ ] Monitor response times

---

## Quick Deployment Commands

### Local Network (Immediate)

```bash
cd /Users/ashish/Jira/jiradocai

# Start Ollama
brew services start ollama

# Edit server address
sed -i '' 's/127.0.0.1/0.0.0.0/g' 3_query_web.py

# Run
source venv/bin/activate && python 3_query_web.py
```

Share with team: `http://YOUR_IP:7860`

### Docker (Production)

```bash
# Build
docker build -t jiradocai .

# Run on any server
docker run -d -p 80:7860 \
  -v ./xray_documentation:/app/docs:ro \
  -v ./chroma_jira_db:/app/chroma_jira_db \
  --name jiradocai \
  jiradocai
```

### Cloud (DigitalOcean/AWS)

```bash
# On the server
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b

git clone YOUR_REPO
cd jiradocai
pip install -r requirements.txt

# Run in background
nohup python 3_query_web.py > output.log 2>&1 &
```

---

## Scaling for Multiple Users

### Horizontal Scaling

Run multiple instances behind a load balancer:

```yaml
# docker-compose.yml
version: '3.8'
services:
  jiradocai-1:
    build: .
    ports:
      - "7861:7860"

  jiradocai-2:
    build: .
    ports:
      - "7862:7860"

  jiradocai-3:
    build: .
    ports:
      - "7863:7860"

  nginx:
    image: nginx
    ports:
      - "80:80"
    # Load balance across instances
```

### Resource Optimization

**For High Traffic:**
- Use faster model: `ollama pull llama3.1:8b-q4` (quantized, faster)
- Add Redis caching for frequent queries
- Use Nginx caching
- Add CDN for static assets

---

## Cost Estimation

### Self-Hosted (DigitalOcean/AWS)

| Component | Cost/Month |
|-----------|------------|
| Server (4GB RAM) | $6-12 |
| Storage (50GB) | $1-2 |
| Bandwidth | Usually free |
| Domain name | $10-15/year |
| SSL Certificate | Free (Let's Encrypt) |
| **Total** | **~$7-15/month** |

### Serverless (Google Cloud Run)

| Usage | Cost/Month |
|-------|------------|
| Light (100 queries/day) | $0.50-2 |
| Medium (1000 queries/day) | $5-15 |
| Heavy (10000 queries/day) | $30-50 |

### Free Options

1. **Gradio Share**: Free, 72-hour links
2. **Fly.io**: Free tier available
3. **Render.com**: Free tier with limitations
4. **Your own computer**: $0 (local network only)

---

## Example: Deploy to Render.com (Free)

1. **Push to GitHub**
```bash
cd /Users/ashish/Jira/jiradocai
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO
git push -u origin main
```

2. **Create render.yaml**
```yaml
services:
  - type: web
    name: jiradocai
    env: python
    buildCommand: "pip install -r requirements.txt && playwright install chromium && ollama pull llama3.1:8b"
    startCommand: "python 3_query_web.py"
    envVars:
      - key: PORT
        value: 7860
```

3. **Deploy on Render.com**
   - Sign up at render.com
   - Connect GitHub repo
   - Deploy
   - Get URL: `https://jiradocai.onrender.com`

---

## Making It Production-Ready

### Add Monitoring

```python
# Add to 3_query_web.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('queries.log'),
        logging.StreamHandler()
    ]
)

def chat_with_sources(message, history):
    logging.info(f"Query: {message}")
    response = query_engine.query(message)
    logging.info(f"Response length: {len(response.response)}")
    return response
```

### Add Rate Limiting

```python
from functools import lru_cache
import time

# Simple rate limiting
query_times = {}

def rate_limit(user_id, max_queries=10, window=60):
    """Allow max_queries per window (seconds)"""
    now = time.time()
    if user_id not in query_times:
        query_times[user_id] = []

    # Remove old queries
    query_times[user_id] = [t for t in query_times[user_id] if now - t < window]

    if len(query_times[user_id]) >= max_queries:
        return False

    query_times[user_id].append(now)
    return True
```

### Add Analytics

```python
# Track popular questions
from collections import Counter

question_counter = Counter()

def chat_with_sources(message, history):
    question_counter[message] += 1
    # ... rest of code

# Export stats
def get_stats():
    return {
        'total_queries': sum(question_counter.values()),
        'unique_questions': len(question_counter),
        'top_questions': question_counter.most_common(10)
    }
```

---

## Recommended Deployment Path

### For Small Team (5-20 users)

**Option**: Docker on DigitalOcean
- **Cost**: ~$12/month
- **Setup time**: 30 minutes
- **Reliability**: High
- **Maintenance**: Low

### For Company-Wide (50-500 users)

**Option**: Kubernetes on Cloud
- **Cost**: ~$50-200/month
- **Setup time**: 2-4 hours
- **Reliability**: Very high
- **Maintenance**: Medium
- **Auto-scaling**: Yes

### For Public Access (Anyone)

**Option**: Cloud Run + CDN
- **Cost**: Pay per use ($10-50/month)
- **Setup time**: 1 hour
- **Reliability**: Very high
- **Maintenance**: Very low
- **Global**: Yes

---

## Quick Start: Deploy to Local Network NOW

```bash
cd /Users/ashish/Jira/jiradocai

# 1. Update server binding
python -c "
import sys
content = open('3_query_web.py').read()
content = content.replace('server_name=\"127.0.0.1\"', 'server_name=\"0.0.0.0\"')
open('3_query_web.py', 'w').write(content)
"

# 2. Restart
lsof -ti:7860 | xargs kill -9 2>/dev/null
source venv/bin/activate && python 3_query_web.py &

# 3. Get your IP
echo "Share this URL with your team:"
echo "http://$(ipconfig getifaddr en0):7860"
```

---

## Security Best Practices

### 1. Add Password Protection

```python
# Simple auth in Gradio
demo = gr.ChatInterface(
    chat_with_sources,
    ...,
).launch(
    auth=("username", "password"),  # Add this
    ...
)
```

### 2. Use HTTPS

Always use SSL/TLS for production deployments.

### 3. Firewall Rules

```bash
# Allow only your company IP range
sudo ufw allow from 192.168.1.0/24 to any port 7860
sudo ufw enable
```

### 4. Regular Updates

```bash
# Update Ollama model
ollama pull llama3.1:8b

# Update Python dependencies
pip install --upgrade -r requirements.txt
```

---

## Troubleshooting Deployment

### Can't access from other computers

```bash
# Check firewall
sudo ufw status

# Check if binding to 0.0.0.0
lsof -i :7860

# Check server is reachable
ping YOUR_SERVER_IP
```

### Slow responses

```bash
# Use smaller model
ollama pull llama3.1:8b-q4

# Or use GPU
# Edit scripts to use device="cuda"
```

### Out of memory

```bash
# Monitor usage
docker stats

# Increase Docker memory limit
# Or use smaller model: ollama pull phi3
```

---

## Next Steps

**Choose your deployment:**

1. **Quick team share**: Use Option 1 (Local Network)
2. **Demo/testing**: Use Option 2 (Gradio Share)
3. **Production**: Use Option 3 or 4 (Docker/Cloud)

**Want help with a specific deployment?** Let me know which option you'd like and I can help set it up!

---

## Production Checklist

- [ ] Ollama running as service
- [ ] JiraDocAI running as service/container
- [ ] Firewall configured
- [ ] HTTPS enabled
- [ ] Monitoring set up
- [ ] Backups configured (ChromaDB)
- [ ] Authentication added (if public)
- [ ] Rate limiting configured
- [ ] Logging enabled
- [ ] Documentation for users

---

**Ready to deploy?** Start with Option 1 for immediate local network sharing!

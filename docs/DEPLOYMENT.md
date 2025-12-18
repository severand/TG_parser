# Deployment Guide

## Local Development

```bash
git clone https://github.com/severand/TG_parser.git
cd TG_parser
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# CLI
python main.py search --channels "@python" --keywords "test"

# API (requires fastapi)
pip install fastapi uvicorn
python -m uvicorn api.main:app --reload
```

## Docker Deployment

### Build Image

```bash
docker build -t tg-parser:1.0 .
```

### Run Container

```bash
docker run -p 8000:8000 -v results:/app/results tg-parser:1.0
```

### Docker Compose

```bash
docker-compose up -d
```

## Production Deployment

### 1. Using Gunicorn

```bash
pip install gunicorn
gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 2. Using Nginx Reverse Proxy

```nginx
upstream app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Using Kubernetes

```bash
kubectl apply -f k8s/deployment.yml
kubectl expose deployment tg-parser --type=LoadBalancer --port=8000
```

## Environment Variables

```bash
export MAX_WORKERS=4
export TIMEOUT=10
export MAX_RETRIES=3
export LOG_LEVEL=INFO
```

## Health Checks

```bash
curl http://localhost:8000/health
```

## Monitoring

- Logs: `/var/log/tg-parser/`
- Metrics: `/metrics` (Prometheus-compatible)
- Health: `/health`

## Performance Tuning

- Increase `MAX_WORKERS` for parallel channels
- Use caching for frequent queries
- Enable compression on reverse proxy
- Use CDN for static content

---

**Last Updated:** 2025-12-18

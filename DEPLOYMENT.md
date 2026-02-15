# Deployment Guide

This guide covers different deployment scenarios for the Codebase Intelligence Analyzer.

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [CI/CD Integration](#cicd-integration)
6. [Offline/Air-Gapped Deployment](#offlineair-gapped-deployment)

## Local Development Setup

### Prerequisites

- Python 3.8+
- pip
- git

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/davidzongo/codebase-intelligence-analyzer.git
cd codebase-intelligence-analyzer

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install package in development mode
pip install -e .

# 6. Verify installation
codebase-analyze --version
```

### First Run

```bash
# Index a sample project
codebase-analyze index ./examples

# Test query (without LLM)
codebase-analyze query "code parser" --no-llm

# View statistics
codebase-analyze stats
```

## Production Deployment

### System Requirements

**Minimum**:
- CPU: 2 cores
- RAM: 4 GB
- Disk: 10 GB
- Network: Optional (for LLM features)

**Recommended**:
- CPU: 4+ cores
- RAM: 8 GB+
- Disk: 50 GB+
- SSD for vector database

### Installation

```bash
# 1. Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv git

# 2. Create application directory
sudo mkdir -p /opt/codebase-analyzer
sudo chown $USER:$USER /opt/codebase-analyzer
cd /opt/codebase-analyzer

# 3. Clone and install
git clone https://github.com/davidzongo/codebase-intelligence-analyzer.git .
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# 4. Create data directory
mkdir -p /opt/codebase-analyzer/data

# 5. Configure environment
cp .env.example .env
# Edit .env with your configuration
```

### Configuration

Edit `/opt/codebase-analyzer/.env`:

```bash
# Database location
DB_PATH=/opt/codebase-analyzer/data/chroma_db

# OpenAI API Key (optional)
OPENAI_API_KEY=your-key-here

# Model selection
OPENAI_MODEL=gpt-3.5-turbo
```

### Running as a Service

Create `/etc/systemd/system/codebase-analyzer.service`:

```ini
[Unit]
Description=Codebase Intelligence Analyzer
After=network.target

[Service]
Type=simple
User=analyzer
WorkingDirectory=/opt/codebase-analyzer
Environment="PATH=/opt/codebase-analyzer/venv/bin"
EnvironmentFile=/opt/codebase-analyzer/.env
ExecStart=/opt/codebase-analyzer/venv/bin/codebase-analyze index /path/to/codebase
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable codebase-analyzer
sudo systemctl start codebase-analyzer
```

## Docker Deployment

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install package
RUN pip install -e .

# Create data directory
RUN mkdir -p /data

# Set environment variables
ENV DB_PATH=/data/chroma_db
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["codebase-analyze", "--help"]
```

### Build and Run

```bash
# Build image
docker build -t codebase-analyzer:latest .

# Run indexing
docker run -v /path/to/codebase:/codebase \
           -v /path/to/data:/data \
           codebase-analyzer:latest \
           index /codebase

# Run query
docker run -v /path/to/data:/data \
           -e OPENAI_API_KEY=${OPENAI_API_KEY} \
           codebase-analyzer:latest \
           query "how does authentication work?"
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  analyzer:
    build: .
    container_name: codebase-analyzer
    volumes:
      - ./codebase:/codebase:ro
      - ./data:/data
    environment:
      - DB_PATH=/data/chroma_db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    command: index /codebase
```

Run:

```bash
docker-compose up
```

## Cloud Deployment

### AWS Deployment

#### EC2 Instance

```bash
# 1. Launch EC2 instance (Amazon Linux 2 or Ubuntu)
# Instance type: t3.medium or larger
# Storage: 50 GB EBS

# 2. Connect to instance
ssh -i your-key.pem ec2-user@your-instance-ip

# 3. Install dependencies
sudo yum update -y
sudo yum install python3 python3-pip git -y

# 4. Follow production deployment steps
```

#### S3 for Data Storage

```python
# Custom storage backend (example)
import boto3

class S3VectorStore:
    def __init__(self, bucket_name):
        self.s3 = boto3.client('s3')
        self.bucket = bucket_name
    
    # Implement storage interface
```

### Google Cloud Deployment

#### Compute Engine

```bash
# 1. Create VM instance
gcloud compute instances create codebase-analyzer \
  --machine-type=e2-standard-2 \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB

# 2. SSH to instance
gcloud compute ssh codebase-analyzer

# 3. Follow production deployment steps
```

### Azure Deployment

```bash
# 1. Create VM
az vm create \
  --resource-group MyResourceGroup \
  --name codebase-analyzer \
  --image UbuntuLTS \
  --size Standard_D2s_v3 \
  --admin-username azureuser \
  --generate-ssh-keys

# 2. Connect and setup
ssh azureuser@your-vm-ip
# Follow production deployment steps
```

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/analyze.yml`:

```yaml
name: Code Analysis

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  analyze:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install Analyzer
      run: |
        pip install codebase-intelligence-analyzer
    
    - name: Index Codebase
      run: |
        codebase-analyze index . --db-path ./analysis_db
    
    - name: Query for Issues
      run: |
        codebase-analyze query "potential security issues" \
          --db-path ./analysis_db \
          --no-llm
    
    - name: Upload Analysis
      uses: actions/upload-artifact@v3
      with:
        name: code-analysis
        path: ./analysis_db
```

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
stages:
  - analyze

code_analysis:
  stage: analyze
  image: python:3.11
  script:
    - pip install codebase-intelligence-analyzer
    - codebase-analyze index . --db-path ./analysis_db
    - codebase-analyze stats --db-path ./analysis_db
  artifacts:
    paths:
      - analysis_db/
    expire_in: 1 week
```

### Jenkins

```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install codebase-intelligence-analyzer'
            }
        }
        
        stage('Index') {
            steps {
                sh 'codebase-analyze index . --db-path ./analysis_db'
            }
        }
        
        stage('Analyze') {
            steps {
                sh 'codebase-analyze query "security concerns" --no-llm'
            }
        }
    }
}
```

## Offline/Air-Gapped Deployment

For environments without internet access:

### Pre-download Dependencies

On a machine with internet:

```bash
# 1. Download all packages
pip download \
  -r requirements.txt \
  -d ./packages/

# 2. Download embedding model
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
model.save('./models/all-MiniLM-L6-v2')
"

# 3. Create deployment package
tar -czf codebase-analyzer-offline.tar.gz \
  ./packages/ \
  ./models/ \
  ./src/ \
  ./setup.py \
  ./requirements.txt
```

### Install Offline

On air-gapped machine:

```bash
# 1. Extract package
tar -xzf codebase-analyzer-offline.tar.gz

# 2. Install dependencies
pip install --no-index --find-links=./packages/ -r requirements.txt

# 3. Install application
pip install -e .

# 4. Configure to use local model
export SENTENCE_TRANSFORMERS_HOME=./models/

# 5. Use without LLM
codebase-analyze index ./codebase --db-path ./db
codebase-analyze query "question" --no-llm --db-path ./db
```

## Monitoring and Maintenance

### Logging

Configure logging in production:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/codebase-analyzer/app.log'),
        logging.StreamHandler()
    ]
)
```

### Monitoring Metrics

Key metrics to monitor:
- Indexing time
- Query response time
- Database size
- Memory usage
- API call costs (if using LLM)

### Backup

```bash
# Backup vector database
tar -czf backup-$(date +%Y%m%d).tar.gz /data/chroma_db

# Restore
tar -xzf backup-20240115.tar.gz -C /data/
```

### Updates

```bash
# Update to latest version
cd /opt/codebase-analyzer
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
pip install -e .

# Re-index if schema changed
codebase-analyze index /path/to/codebase
```

## Security Considerations

### API Keys

```bash
# Never commit API keys
# Use environment variables or secrets management

# AWS Secrets Manager
export OPENAI_API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id openai-key --query SecretString --output text)

# HashiCorp Vault
export OPENAI_API_KEY=$(vault kv get -field=key secret/openai)
```

### Network Security

```bash
# Firewall rules (allow only necessary ports)
sudo ufw allow 22/tcp  # SSH
sudo ufw enable

# No inbound ports needed for CLI usage
```

### File Permissions

```bash
# Restrict access to sensitive files
chmod 600 .env
chmod 700 data/

# Run as non-root user
sudo useradd -r -s /bin/false analyzer
sudo chown -R analyzer:analyzer /opt/codebase-analyzer
```

## Troubleshooting

### Common Issues

1. **Out of memory**: Increase system RAM or process files in batches
2. **Slow indexing**: Use SSD, increase CPU cores
3. **Network timeouts**: Pre-download models, use offline mode
4. **Permission errors**: Check file/directory permissions

### Debug Mode

```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
codebase-analyze index ./codebase
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/davidzongo/codebase-intelligence-analyzer/issues
- Documentation: See README.md and USAGE.md

## Conclusion

Choose the deployment method that best fits your needs:
- **Local**: Development and testing
- **Production**: Long-running analysis server
- **Docker**: Containerized, portable deployment
- **Cloud**: Scalable, managed infrastructure
- **CI/CD**: Automated analysis in pipelines
- **Offline**: Secure, air-gapped environments

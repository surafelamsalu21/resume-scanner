# 🚀 Resume AI Backend - Deployment Guide

This guide will help you deploy the Resume AI Backend using Docker, following the same workflow you used for your previous successful deployment.

## 📋 Prerequisites

- Docker and Docker Compose installed on your server
- Git access to your repository
- OpenAI API key
- SSL certificates (optional, for HTTPS)

## 🔧 Local Development Setup

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <your-repository-url>
cd resume-ai-backend-3

# Copy environment template
cp env.example .env

# Edit environment variables
nano .env
```

### 2. Configure Environment Variables

Edit `.env` file with your actual values:

```bash
# Application Settings
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-here
DEBUG=True

# Database
DATABASE_URL=postgresql://postgres:your_password@db:5432/resume_ai
DB_PASSWORD=your_secure_password
POSTGRES_DB=resume_ai
POSTGRES_USER=postgres

# JWT Authentication
JWT_SECRET_KEY=your-jwt-secret-key

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# Server Configuration
PORT=5001
WORKERS=2
THREADS=1
TIMEOUT=60
```

### 3. Start Development Environment

```bash
# Start with development configuration
docker-compose -f docker/docker-compose.dev.yaml up -d

# Check logs
docker-compose -f docker/docker-compose.dev.yaml logs -f

# Access the application  
curl http://localhost:5001/health
```

### 4. Test Local Development

```bash
# Check if all services are running
docker-compose -f docker/docker-compose.dev.yaml ps

# Access pgAdmin (if needed)
# URL: http://localhost:5051
# Email: admin@admin.com
# Password: admin

# Stop development environment
docker-compose -f docker/docker-compose.dev.yaml down
```

## 🌐 Production Deployment

### 1. Prepare Server Environment

```bash
# On your server, install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone Repository on Server

```bash
# Clone your repository
git clone <your-repository-url>
cd resume-ai-backend-3

# Create production environment file
cp env.example .env
```

### 3. Configure Production Environment

Edit `.env` for production:

```bash
# Production Configuration
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=your-production-secret-key-change-this
DEBUG=False

# Strong Database Password
DATABASE_URL=postgresql://postgres:very_strong_password@db:5432/resume_ai
DB_PASSWORD=very_strong_password
POSTGRES_DB=resume_ai
POSTGRES_USER=postgres

# Secure JWT Key
JWT_SECRET_KEY=your-production-jwt-secret-key

# OpenAI API
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# Production Server Settings  
PORT=8081
HOST=0.0.0.0
WORKERS=4
THREADS=2
TIMEOUT=120

# Security
CORS_ORIGINS=your-domain.com,www.your-domain.com
LOG_LEVEL=INFO
```

### 4. Deploy with Docker Compose

```bash
# Start production services
docker-compose -f docker/docker-compose.yaml up -d

# Check deployment status
docker-compose -f docker/docker-compose.yaml ps

# Monitor logs
docker-compose -f docker/docker-compose.yaml logs -f
```

### 5. Verify Deployment

```bash
# Health check
curl http://31.220.31.112:8081/health

# Check application
curl http://31.220.31.112:8081/

# Check database connection (external PostgreSQL server)
psql -h 31.220.31.112 -U resume_user -d resume_ai -c "SELECT 1;"
```

## 🔄 Deployment Workflow (Same as Your Previous Project)

### Step 1: Local Testing
```bash
# Test locally first
docker-compose -f docker/docker-compose.dev.yaml up -d
# Verify everything works
# Make any necessary changes
docker-compose -f docker/docker-compose.dev.yaml down
```

### Step 2: Commit and Push
```bash
# Add changes to git
git add .
git commit -m "feat: production deployment ready"
git push origin main
```

### Step 3: Server Deployment
```bash
# On your server
git pull origin main

# Stop existing containers (if any)
docker-compose -f docker/docker-compose.yaml down

# Rebuild and start
docker-compose -f docker/docker-compose.yaml up --build -d

# Verify deployment
docker-compose -f docker/docker-compose.yaml logs -f
```

## 🔧 Environment Configurations

### Development (.env for local development)
```bash
FLASK_ENV=development
DEBUG=True
PORT=5001
WORKERS=2
LOG_LEVEL=DEBUG
```

### Production (.env for server)
```bash
FLASK_ENV=production
DEBUG=False
PORT=5000
WORKERS=4
LOG_LEVEL=INFO
```

## 📊 Monitoring and Maintenance

### Check Application Status
```bash
# Container status
docker-compose ps

# Application logs
docker-compose logs backend

# Database logs
docker-compose logs db

# Redis logs
docker-compose logs redis
```

### Database Backup
```bash
# Create database backup
docker-compose exec db pg_dump -U postgres resume_ai > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker-compose exec -T db psql -U postgres resume_ai < backup_file.sql
```

### Update Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build -d
```

## 🛡️ Security Considerations

### Environment Variables
- Never commit `.env` files to Git
- Use strong passwords for database
- Generate secure JWT secrets
- Restrict CORS origins in production

### Network Security
```bash
# Only expose necessary ports
# In production, use a reverse proxy (nginx)
# Enable SSL/TLS certificates
```

### Regular Updates
```bash
# Update base images regularly
docker-compose pull
docker-compose up -d --force-recreate
```

## 🚨 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :5000

# Kill the process
sudo kill -9 <PID>
```

#### Database Connection Issues
```bash
# Check database container
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up -d
```

#### Application Won't Start
```bash
# Check application logs
docker-compose logs backend

# Rebuild containers
docker-compose up --build -d
```

### Logs Location
```bash
# Application logs
docker-compose logs backend

# System logs
journalctl -u docker

# Container logs
docker logs resume_ai_backend
```

## 📱 Health Monitoring

### Built-in Health Checks
```bash
# Application health
curl http://localhost:5000/health

# Database health
docker-compose exec db pg_isready -U postgres

# Redis health
docker-compose exec redis redis-cli ping
```

### Monitoring URLs
- Health Check: `http://31.220.31.112:8081/health`
- Application: `http://31.220.31.112:8081/`  
- Admin Panel: `http://31.220.31.112:8081/admin/login`

## 🔄 Backup Strategy

### Automated Backups
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec db pg_dump -U postgres resume_ai > /backups/resume_ai_$DATE.sql
find /backups -name "resume_ai_*.sql" -mtime +7 -delete
```

### Volume Backups
```bash
# Backup volumes
docker run --rm -v resume_ai_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data_backup.tar.gz /data
docker run --rm -v resume_ai_uploads:/data -v $(pwd):/backup alpine tar czf /backup/uploads_backup.tar.gz /data
```

---

## ✅ Success Checklist

- [ ] Local development environment working
- [ ] Environment variables configured
- [ ] Application accessible on server
- [ ] Health endpoint responding
- [ ] Database connectivity verified
- [ ] File uploads working
- [ ] Admin panel accessible
- [ ] SSL configured (if applicable)
- [ ] Backups configured
- [ ] Monitoring setup

---

**🎉 Your Resume AI Backend is now ready for production deployment using the same workflow as your previous successful project!**

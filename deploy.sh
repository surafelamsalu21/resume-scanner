#!/bin/bash

# ==================================
# RESUME AI BACKEND - DEPLOYMENT SCRIPT
# ==================================
# This script automates the deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in correct directory
if [ ! -f "run.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev     - Start development environment"
    echo "  prod    - Start production environment"
    echo "  stop    - Stop all services"
    echo "  logs    - Show application logs"
    echo "  health  - Check application health"
    echo "  backup  - Create database backup"
    echo "  update  - Update and restart services"
    echo "  clean   - Clean up unused Docker resources"
    echo ""
}

# Function to check if .env exists
check_env() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f "env.example" ]; then
            cp env.example .env
            print_warning "Please edit .env file with your actual values before proceeding"
            return 1
        else
            print_error "env.example not found. Cannot create .env file"
            exit 1
        fi
    fi
    return 0
}

# Function to start development environment
start_dev() {
    print_status "Starting development environment..."
    check_env || exit 1
    
    # Use development compose file
    docker-compose -f docker/docker-compose.dev.yaml up -d
    
    print_status "Waiting for services to start..."
    sleep 10
    
    # Check health
    if curl -f http://localhost:5001/health > /dev/null 2>&1; then
        print_success "Development environment started successfully!"
        print_status "Application: http://localhost:5001"
        print_status "pgAdmin: http://localhost:5051 (admin@admin.com / admin)"
        print_status "Database: localhost:5433"
        print_status "Redis: localhost:6380"
    else
        print_error "Health check failed. Check logs with: $0 logs"
        exit 1
    fi
}

# Function to start production environment
start_prod() {
    print_status "Starting production environment..."
    check_env || exit 1
    
    # Check if running as production
    if grep -q "FLASK_ENV=development" .env; then
        print_warning "Warning: .env is configured for development"
        print_warning "Make sure to update FLASK_ENV=production for production deployment"
    fi
    
    # Use production compose file
    docker-compose -f docker/docker-compose.yaml up -d --build
    
    print_status "Waiting for services to start..."
    sleep 15
    
    # Check health
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        print_success "Production environment started successfully!"
        print_status "Application: http://localhost:5000"
        print_status "Database: localhost:5432"
        print_status "Redis: localhost:6379"
    else
        print_error "Health check failed. Check logs with: $0 logs"
        exit 1
    fi
}

# Function to stop services
stop_services() {
    print_status "Stopping all services..."
    
    # Stop both development and production services
    if [ -f "docker/docker-compose.dev.yaml" ]; then
        docker-compose -f docker/docker-compose.dev.yaml down
    fi
    
    if [ -f "docker/docker-compose.yaml" ]; then
        docker-compose -f docker/docker-compose.yaml down
    fi
    
    print_success "All services stopped"
}

# Function to show logs
show_logs() {
    print_status "Showing application logs..."
    
    # Try production first, then development
    if docker ps | grep -q "resume_ai_backend"; then
        docker-compose -f docker/docker-compose.yaml logs -f backend
    elif docker ps | grep -q "resume_ai_backend_dev"; then
        docker-compose -f docker/docker-compose.dev.yaml logs -f backend
    else
        print_error "No running containers found"
        exit 1
    fi
}

# Function to check health
check_health() {
    print_status "Checking application health..."
    
    # Check production first
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        print_success "Production environment is healthy"
        curl -s http://localhost:5000/health | python3 -m json.tool
    elif curl -f http://localhost:5001/health > /dev/null 2>&1; then
        print_success "Development environment is healthy"
        curl -s http://localhost:5001/health | python3 -m json.tool
    else
        print_error "Application health check failed"
        print_status "Checking container status..."
        docker ps --filter "name=resume_ai"
        exit 1
    fi
}

# Function to create backup
create_backup() {
    print_status "Creating database backup..."
    
    BACKUP_DIR="backups"
    mkdir -p $BACKUP_DIR
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/resume_ai_backup_$TIMESTAMP.sql"
    
    # Try production first, then development
    if docker ps | grep -q "resume_ai_db"; then
        docker-compose -f docker/docker-compose.yaml exec -T db pg_dump -U postgres resume_ai > $BACKUP_FILE
    elif docker ps | grep -q "resume_ai_db_dev"; then
        docker-compose -f docker/docker-compose.dev.yaml exec -T db pg_dump -U postgres resume_ai > $BACKUP_FILE
    else
        print_error "No database container found"
        exit 1
    fi
    
    print_success "Backup created: $BACKUP_FILE"
    
    # Keep only last 7 backups
    find $BACKUP_DIR -name "resume_ai_backup_*.sql" -mtime +7 -delete 2>/dev/null || true
}

# Function to update services
update_services() {
    print_status "Updating services..."
    
    # Pull latest changes
    git pull origin main
    
    # Rebuild and restart
    if docker ps | grep -q "resume_ai_backend"; then
        print_status "Updating production environment..."
        docker-compose -f docker/docker-compose.yaml down
        docker-compose -f docker/docker-compose.yaml up -d --build
        sleep 15
        if curl -f http://localhost:5000/health > /dev/null 2>&1; then
            print_success "Production environment updated successfully!"
        else
            print_error "Update failed. Check logs."
        fi
    elif docker ps | grep -q "resume_ai_backend_dev"; then
        print_status "Updating development environment..."
        docker-compose -f docker/docker-compose.dev.yaml down
        docker-compose -f docker/docker-compose.dev.yaml up -d --build
        sleep 10
        if curl -f http://localhost:5001/health > /dev/null 2>&1; then
            print_success "Development environment updated successfully!"
        else
            print_error "Update failed. Check logs."
        fi
    else
        print_error "No running services found to update"
        exit 1
    fi
}

# Function to clean up Docker resources
clean_docker() {
    print_status "Cleaning up Docker resources..."
    
    # Remove unused containers, networks, images
    docker system prune -f
    
    # Remove unused volumes (be careful with this)
    read -p "Remove unused volumes? This may delete data. [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker volume prune -f
        print_success "Volumes cleaned"
    fi
    
    print_success "Docker cleanup completed"
}

# Main script logic
case "${1:-}" in
    "dev")
        start_dev
        ;;
    "prod")
        start_prod
        ;;
    "stop")
        stop_services
        ;;
    "logs")
        show_logs
        ;;
    "health")
        check_health
        ;;
    "backup")
        create_backup
        ;;
    "update")
        update_services
        ;;
    "clean")
        clean_docker
        ;;
    *)
        show_usage
        exit 1
        ;;
esac

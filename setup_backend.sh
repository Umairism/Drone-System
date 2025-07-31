#!/bin/bash

# Surveillance Drone System - Backend Setup Script
# This script sets up the Flask backend environment and dependencies

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║            Surveillance Drone System - Backend              ║"
echo "║                    Setup and Installation                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Python is installed
print_status "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_success "Python $PYTHON_VERSION detected"

# Check if pip is installed
print_status "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip3."
    exit 1
fi
print_success "pip3 is available"

# Get the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"

print_status "Project directory: $PROJECT_DIR"
print_status "Backend directory: $BACKEND_DIR"

# Navigate to backend directory
cd "$BACKEND_DIR" || exit 1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        print_success "Virtual environment created successfully"
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        print_success "Dependencies installed successfully"
    else
        print_error "Failed to install some dependencies"
        print_warning "You may need to install some system packages first"
    fi
else
    print_error "requirements.txt not found"
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs data data/recordings data/missions uploads temp
print_success "Directories created"

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating environment configuration file..."
    cat > .env << EOF
# Flask Configuration
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///data/surveillance_drone.db

# Secret Keys (Change these in production!)
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-key-change-in-production

# Redis Configuration (for session storage and caching)
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/flask_app.log

# CORS Settings
CORS_ORIGINS=*

# SocketIO Settings
SOCKETIO_ASYNC_MODE=eventlet

# File Upload Settings
MAX_CONTENT_LENGTH=16777216  # 16MB
UPLOAD_FOLDER=uploads

# Video Settings
VIDEO_RECORD_PATH=data/recordings
VIDEO_STREAM_PORT=8000

# Drone Settings
DRONE_CONNECTION_STRING=udp:127.0.0.1:14550
DRONE_BAUD_RATE=57600
DRONE_TIMEOUT=30

# Security Settings
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
EOF
    print_success "Environment file created (.env)"
    print_warning "Please review and update the .env file with your specific settings"
else
    print_warning ".env file already exists"
fi

# Make run script executable
chmod +x run.py

print_success "Backend setup completed successfully!"
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                        Next Steps                           ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  1. Review and update the .env file with your settings      ║"
echo "║  2. Start the backend server:                               ║"
echo "║     cd backend && source venv/bin/activate                  ║"
echo "║     python run.py                                           ║"
echo "║                                                              ║"
echo "║  3. Or use the startup script:                              ║"
echo "║     ./start_backend.sh                                      ║"
echo "║                                                              ║"
echo "║  The API will be available at:                              ║"
echo "║  http://localhost:5000/api                                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"

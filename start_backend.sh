#!/bin/bash

# Surveillance Drone System - Backend Startup Script
# This script starts the Flask backend server

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║            Surveillance Drone System - Backend              ║"
echo "║                      Starting Server                        ║"
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

# Get the project directory and navigate to backend
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"

print_status "Project directory: $PROJECT_DIR"
print_status "Backend directory: $BACKEND_DIR"

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    print_error "Backend directory not found: $BACKEND_DIR"
    print_status "Please run setup_backend.sh first"
    exit 1
fi

# Navigate to backend directory
cd "$BACKEND_DIR" || exit 1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found"
    print_status "Please run setup_backend.sh first to create the virtual environment"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
print_status "Checking if Flask is installed..."
if ! python -c "import flask" 2>/dev/null; then
    print_error "Flask is not installed"
    print_status "Installing requirements..."
    pip install -r requirements.txt
fi

# Load environment variables if .env exists
if [ -f ".env" ]; then
    print_status "Loading environment variables from .env"
    export $(cat .env | grep -v '#' | xargs)
fi

# Set default values if not set
export FLASK_ENV=${FLASK_ENV:-development}
export FLASK_HOST=${FLASK_HOST:-0.0.0.0}
export FLASK_PORT=${FLASK_PORT:-5000}

print_status "Environment: $FLASK_ENV"
print_status "Host: $FLASK_HOST"
print_status "Port: $FLASK_PORT"

# Check if port is available
if lsof -Pi :$FLASK_PORT -sTCP:LISTEN -t >/dev/null; then
    print_warning "Port $FLASK_PORT is already in use"
    print_status "Please stop the existing service or change the port in .env file"
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs data data/recordings data/missions uploads temp

# Start the Flask application
print_success "Starting Flask backend server..."
echo ""
print_status "Press Ctrl+C to stop the server"
echo ""

# Check if we're in development mode
if [ "$FLASK_ENV" = "development" ]; then
    # Development mode - use Flask development server
    python run.py
else
    # Production mode - use gunicorn
    print_status "Starting production server with gunicorn..."
    gunicorn --worker-class eventlet -w 1 --bind $FLASK_HOST:$FLASK_PORT run:app
fi

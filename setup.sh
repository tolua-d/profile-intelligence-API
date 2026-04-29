#!/bin/bash

# Profile Intelligence Platform - Setup Script
# This script sets up the backend, CLI, and web portal

set -e

echo "======================================"
echo "Profile Intelligence Platform Setup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}→${NC} $1"
}

# Check prerequisites
print_info "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3.10+"
    exit 1
fi
print_status "Python found: $(python3 --version)"

if ! command -v pip &> /dev/null; then
    print_error "pip not found. Please install pip"
    exit 1
fi
print_status "pip found"

echo ""
echo "======================================"
echo "Setting up Backend"
echo "======================================"
echo ""

cd "$(dirname "$0")"

# Create virtual environment
if [ ! -d ".venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv .venv
    print_status "Virtual environment created"
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
print_info "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_status "Dependencies installed"

# Setup environment file
if [ ! -f ".env" ]; then
    print_info "Creating .env file from template..."
    cp .env.example .env
    print_status ".env file created"
    echo ""
    echo -e "${YELLOW}⚠${NC}  Important: Edit .env file with your GitHub OAuth credentials:"
    echo "   - GITHUB_CLIENT_ID"
    echo "   - GITHUB_CLIENT_SECRET"
    echo "   - DATABASE_URL"
    echo ""
fi

# Run migrations
print_info "Running migrations..."
python manage.py migrate
print_status "Migrations completed"

# Create logs directory
mkdir -p logs
print_status "Logs directory created"

echo ""
print_status "Backend setup completed!"

echo ""
echo "======================================"
echo "Next Steps"
echo "======================================"
echo ""
print_info "1. Edit .env file with your GitHub OAuth credentials:"
echo "   nano .env"
echo ""
print_info "2. Start backend development server:"
echo "   source .venv/bin/activate"
echo "   python manage.py runserver"
echo ""
print_info "3. Create CLI repository:"
echo "   cd .. && git clone <cli-repo-url>"
echo ""
print_info "4. Create Web Portal repository:"
echo "   cd .. && git clone <web-portal-repo-url>"
echo ""
print_info "5. Check README.md for detailed documentation"
echo ""

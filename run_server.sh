#!/bin/bash

# OneStopRadio Django Development Server
# Runs on port 8000 with auto-reload

echo "🎵 Starting OneStopRadio Django API Server"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update requirements
echo "📋 Installing Python dependencies..."
pip install -r requirements.txt

# Run Django migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist (optional)
if [ "$1" = "--create-admin" ]; then
    echo "👤 Creating Django admin user..."
    python manage.py createsuperuser
fi

# Collect static files (for production)
if [ "$1" = "--prod" ]; then
    echo "📁 Collecting static files..."
    python manage.py collectstatic --noinput
fi

# Start Django development server
echo ""
echo "🚀 Starting Django server on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/api/docs/"
echo "🔧 Admin Panel: http://localhost:8000/admin/"
echo ""
echo "Press Ctrl+C to stop server"
echo ""

python manage.py runserver 0.0.0.0:8000
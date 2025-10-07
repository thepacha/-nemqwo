#!/bin/bash

# VoiceScript AI - Setup Script
echo "🚀 Setting up VoiceScript AI Transcription SaaS..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p database uploads ssl

# Copy environment file
if [ ! -f .env ]; then
    echo "📝 Creating environment file..."
    cp backend/.env.example .env
    echo "⚠️  Please edit .env file with your API keys and configuration"
fi

# Copy frontend environment file
if [ ! -f frontend/.env ]; then
    echo "📝 Creating frontend environment file..."
    cp frontend/.env.example frontend/.env
fi

# Generate JWT secret key
if ! grep -q "your_jwt_secret_key_here" .env; then
    JWT_SECRET=$(openssl rand -hex 32)
    sed -i "s/your_jwt_secret_key_here/$JWT_SECRET/g" .env
    echo "🔑 Generated JWT secret key"
fi

# Set proper permissions
chmod +x scripts/*.sh

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   - OPENAI_API_KEY: Your OpenAI API key"
echo "   - STRIPE_SECRET_KEY: Your Stripe secret key"
echo "   - STRIPE_PUBLISHABLE_KEY: Your Stripe publishable key"
echo ""
echo "2. Run the application:"
echo "   ./scripts/start.sh"
echo ""
echo "3. For production deployment:"
echo "   ./scripts/deploy.sh"
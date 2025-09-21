#!/bin/bash

# Deployment script for dmitrybond.tech
# This script deploys the complete stack including web, Cal.com, and mailcow

set -e

echo "🚀 Starting deployment of dmitrybond.tech..."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p caddy/data
mkdir -p caddy/config
mkdir -p cal
mkdir -p mailcow

# Check if environment files exist
if [ ! -f "cal/.env" ]; then
    echo "⚠️  cal/.env not found. Please copy cal/env.example to cal/.env and configure it."
    exit 1
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check if Caddy is running
if ! docker-compose ps caddy | grep -q "Up"; then
    echo "❌ Caddy service is not running"
    exit 1
fi

# Check if web service is running
if ! docker-compose ps web | grep -q "Up"; then
    echo "❌ Web service is not running"
    exit 1
fi

# Check if Cal.com is running
if ! docker-compose ps cal | grep -q "Up"; then
    echo "❌ Cal.com service is not running"
    exit 1
fi

# Check if PostgreSQL is running
if ! docker-compose ps postgres | grep -q "Up"; then
    echo "❌ PostgreSQL service is not running"
    exit 1
fi

# Check if Redis is running
if ! docker-compose ps redis | grep -q "Up"; then
    echo "❌ Redis service is not running"
    exit 1
fi

echo "✅ All services are running successfully!"

# Display service URLs
echo ""
echo "🌐 Service URLs:"
echo "   Website: https://dmitrybond.tech"
echo "   English booking: https://dmitrybond.tech/en/bookme"
echo "   Russian booking: https://dmitrybond.tech/ru/bookme"
echo "   Cal.com admin: https://dmitrybond.tech/cal"

# Display logs command
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Update services: docker-compose pull && docker-compose up -d"

echo ""
echo "🎉 Deployment completed successfully!"



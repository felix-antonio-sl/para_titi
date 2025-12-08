#!/bin/bash
# scripts/deploy.sh - Helper script for deployment

echo "🚀 Starting Deployment/Restart..."

# 1. Build and Start
echo "📦 Building and starting containers..."
docker compose up -d --build

# 2. Wait for DB
echo "⏳ Waiting for Database to be ready..."
until docker compose exec db pg_isready -U gore -d gore_nuble; do
  echo "   Waiting for DB..."
  sleep 2
done

# 3. Initialize DB (SAFE MODE)
# Only runs if we explicitly ask for it or check if specific table exists?
# For now, we will run the safe init (create_all check)
echo "🛠  Running Database Initialization..."
docker compose exec app python init_db_dev.py

echo "✅ Deployment Complete."
echo "   App accessible at http://localhost (via Nginx)"

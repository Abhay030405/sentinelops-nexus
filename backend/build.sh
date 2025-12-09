#!/usr/bin/env bash

# Build script for Render deployment
set -o errexit  # Exit on error

echo "🔧 Starting build process..."
echo "📦 Upgrading pip..."
pip install --upgrade pip

echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

echo "🎨 Creating necessary directories..."
mkdir -p uploads/documents
mkdir -p uploads/missions
mkdir -p vector_db

echo "✅ Build completed successfully!"
echo "🚀 Ready to start the application!"

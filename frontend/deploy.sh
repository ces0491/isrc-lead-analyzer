#!/bin/bash
# Frontend deployment script for Render

echo "🚀 Building Prism Analytics Engine Frontend..."

# Install dependencies
echo "📦 Installing dependencies..."
npm ci

# Build for production with correct API URL
echo "🔨 Building for production..."
export REACT_APP_API_BASE_URL="https://isrc-analyzer-api.onrender.com/api"
export REACT_APP_PRISM_ENVIRONMENT="production"
export REACT_APP_VERSION="1.0.0"

npm run build

# Copy build files to serve
echo "📁 Preparing build files..."
cp -r build/* .

echo "✅ Frontend build complete!"
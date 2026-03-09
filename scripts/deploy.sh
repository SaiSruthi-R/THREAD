#!/bin/bash
set -e

echo "🚀 Deploying Memory Mapping System..."

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install -r requirements.txt

# Deploy CDK stacks
echo "☁️  Deploying AWS infrastructure..."
cd infrastructure/cdk
pip install -r requirements.txt
cdk bootstrap
cdk deploy --all --require-approval never

# Get API endpoint from CDK outputs
API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name MemoryMappingAPIStack \
  --query 'Stacks[0].Outputs[?OutputKey==`APIEndpoint`].OutputValue' \
  --output text)

echo "✅ API Endpoint: $API_ENDPOINT"

# Update frontend environment
cd ../../frontend
echo "REACT_APP_API_BASE=$API_ENDPOINT" > .env

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
npm install

# Build frontend
echo "🏗️  Building frontend..."
npm run build

echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Run 'python scripts/seed_data.py' to load sample data"
echo "2. Run 'cd frontend && npm start' to start the development server"
echo "3. Open http://localhost:3000 in your browser"

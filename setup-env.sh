#!/bin/bash

# Resume AI Backend - Environment Setup Script
# This script helps you set up the .env file with the correct values

echo "🚀 Resume AI Backend - Environment Setup"
echo "========================================"

# Check if .env exists
if [ -f ".env" ]; then
    echo "✅ .env file found"
    echo "Current .env contents:"
    echo "----------------------"
    cat .env
    echo "----------------------"
    echo ""
    read -p "Do you want to recreate the .env file? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file. Make sure the values are correct!"
        exit 0
    fi
fi

# Create .env file from template
if [ ! -f "env.template" ]; then
    echo "❌ env.template not found! Please make sure you're in the project directory."
    exit 1
fi

echo "📝 Creating .env file from template..."
cp env.template .env

echo ""
echo "✅ .env file created! Now you need to edit it with your actual values:"
echo ""
echo "🔧 Required changes in .env:"
echo "1. SECRET_KEY=your-actual-secret-key"
echo "2. JWT_SECRET_KEY=your-actual-jwt-secret"  
echo "3. OPENAI_API_KEY=your-openai-api-key-from-press-project"
echo "4. POSTGRES_PASSWORD=resume_password_2024"
echo ""
echo "📝 Edit the file now:"
echo "nano .env"
echo ""
echo "🚀 Then run deployment:"
echo "./deploy.sh prod"

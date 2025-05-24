#!/bin/bash
# setup_conda.sh - Setup conda environment for AI Service

set -e

echo "🚀 Setting up AI Service with Conda and PostgreSQL..."

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed. Please install conda first."
    exit 1
fi

# Create conda environment
echo "📦 Creating conda environment 'ai-service'..."
conda create -n ai-service python=3.11 -y

# Activate environment
echo "🔄 Activating conda environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate ai-service

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install additional system dependencies (if needed)
echo "🔧 Installing additional dependencies..."
# For audio processing
pip install librosa soundfile

# Setup database directory
echo "📁 Creating necessary directories..."
mkdir -p temp_audio
mkdir -p logs

# Copy environment file
if [ ! -f .env ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual configuration values!"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Activate the environment: conda activate ai-service"
echo "2. Edit .env file with your Alibaba Cloud and PostgreSQL credentials"
echo "3. Initialize the database: python init_db.py"
echo "4. Run the application: make run"
echo ""
echo "📖 For more information, see README.md"

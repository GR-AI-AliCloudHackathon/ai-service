#!/usr/bin/env bash
# setup_dependencies.sh - Install missing dependencies for Alibaba PostgreSQL connection

echo "==== Installing PostgreSQL dependencies for AI Service ===="

# Check if we're in a conda environment
if [ -z "$CONDA_PREFIX" ]; then
  echo "❌ No active conda environment detected."
  echo "Please activate your conda environment first with:"
  echo "  conda activate ai-service"
  exit 1
fi

echo "✅ Using conda environment: $CONDA_PREFIX"

# Install required packages
echo "Installing required packages..."
pip install "sqlalchemy[asyncio]" asyncpg psycopg2-binary python-dotenv fastapi uvicorn alembic

# Check if PostgreSQL client utilities are available
if ! command -v psql &> /dev/null; then
    echo "Installing PostgreSQL client utilities..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install postgresql
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux (Ubuntu/Debian)
        sudo apt-get update && sudo apt-get install -y postgresql-client
    else
        echo "⚠️ Your OS was not recognized. Please install PostgreSQL client utilities manually."
    fi
fi

# Verify installations
echo "Verifying installations..."

# Check sqlalchemy
python -c "import sqlalchemy; print(f'SQLAlchemy version: {sqlalchemy.__version__}')" || echo "❌ SQLAlchemy not installed correctly"

# Check asyncpg
python -c "import asyncpg; print(f'AsyncPG version: {asyncpg.__version__}')" || echo "❌ AsyncPG not installed correctly"

# Check dotenv
python -c "import dotenv; print(f'python-dotenv version: {dotenv.__version__}')" || echo "❌ python-dotenv not installed correctly"

# Check FastAPI
python -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')" || echo "❌ FastAPI not installed correctly"

# Check uvicorn
python -c "import uvicorn; print(f'Uvicorn version: {uvicorn.__version__}')" || echo "❌ Uvicorn not installed correctly"

# Check alembic
python -c "import alembic; print(f'Alembic version: {alembic.__version__}')" || echo "❌ Alembic not installed correctly"

echo ""
echo "==== Dependencies setup complete ===="
echo "You can now connect to your Alibaba ApsaraDB PostgreSQL by running:"
echo "./connect_alibaba_postgresql.py test"
echo ""
echo "To fully set up the database with sample data, run:"
echo "./connect_alibaba_postgresql.py full"

# Makefile for AI Service with Conda
.PHONY: install run clean test docker-build docker-run setup conda-setup conda-install

# Conda environment setup
conda-setup:
	@echo "🚀 Setting up conda environment..."
	./setup_conda.sh

# Install dependencies in conda environment
conda-install:
	@echo "📦 Installing dependencies in conda environment..."
	conda activate ai-service && pip install -r requirements.txt

# Install dependencies (original pip method)
install:
	pip install -r requirements.txt

# Run the application with conda
conda-run:
	@echo "🚀 Starting AI Service with conda..."
	conda activate ai-service && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run the application (original method)
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run in production mode
run-prod:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Clean temporary files
clean:
	rm -rf temp_audio/*
	rm -rf __pycache__
	find . -name "*.pyc" -delete

# Test the API endpoints
test:
	curl -X GET http://localhost:8000/health
	@echo "\nHealth check completed"

# Build and run with Docker (optional)
docker-build:
	docker build -t goshield .

docker-run:
	docker run -p 8000:8000 --env-file .env goshield

# Setup everything with conda
conda-setup-all: conda-setup
	@echo "📊 Initializing database..."
	conda activate ai-service && python init_db.py
	@echo "✅ AI Service setup completed with conda!"

# Setup everything (original method)
setup: install
	mkdir -p temp_audio
	@echo "GoShield setup completed!"

# Initialize database
init-db:
	@echo "📊 Initializing PostgreSQL database..."
	python init_db.py

# Initialize database with conda
conda-init-db:
	@echo "📊 Initializing PostgreSQL database with conda..."
	conda activate ai-service && python init_db.py

# Tambahkan ke Makefile
test-audio:
	@echo "Testing audio endpoints..."
	@echo "1. Testing high risk audio..."
	curl -s -X POST "http://localhost:8000/api/assessment" \
		-F "audio_file=@test_audio/high.m4a" \
		-F "driver_id=bad_driver" | jq -r '.risk_level'
	
	@echo "2. Testing medium risk audio..."
	curl -s -X POST "http://localhost:8000/api/assessment" \
		-F "audio_file=@test_audio/medium.m4a" \
		-F "driver_id=avg_driver" | jq -r '.risk_level'
	
	@echo "3. Testing low risk audio..."
	curl -s -X POST "http://localhost:8000/api/assessment" \
		-F "audio_file=@test_audio/low.m4a" \
		-F "driver_id=good_driver" | jq -r '.risk_level'

# Test semua sekaligus
test-all: test test-audio
	@echo "All tests completed!"

# Deploy (for VM deployment)
deploy: clean install
	@echo "Deploying GoShield..."
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2

# Deploy with conda
conda-deploy: clean conda-install
	@echo "Deploying GoShield with conda..."
	conda activate ai-service && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2

# Database migration commands
db-migrate:
	@echo "🔄 Running database migrations..."
	alembic upgrade head

db-revision:
	@echo "📝 Creating new migration..."
	alembic revision --autogenerate -m "$(message)"

db-history:
	@echo "📜 Migration history:"
	alembic history

db-downgrade:
	@echo "⬇️ Downgrading database..."
	alembic downgrade $(revision)

# Database migration commands with conda
conda-db-migrate:
	@echo "🔄 Running database migrations with conda..."
	conda activate ai-service && alembic upgrade head

conda-db-revision:
	@echo "📝 Creating new migration with conda..."
	conda activate ai-service && alembic revision --autogenerate -m "$(message)"
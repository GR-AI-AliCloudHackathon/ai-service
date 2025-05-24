# Makefile
.PHONY: install run clean test docker-build docker-run

# Install dependencies
install:
	pip install -r requirements.txt

# Run the application
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

# Setup everything
setup: install
	mkdir -p temp_audio
	@echo "GoShield setup completed!"

# Deploy (for VM deployment)
deploy: clean install
	@echo "Deploying GoShield..."
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2

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
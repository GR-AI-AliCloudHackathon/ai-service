# AI Service - PostgreSQL Schema & Alibaba Cloud Integration

This document outlines the PostgreSQL database schema and integration with Alibaba ApsaraDB PostgreSQL for the AI Service project.

## Database Schema Overview

The database is designed to store audio assessments, incidents, driver data, and system logs for the ride safety pipeline.

### Core Tables

1. **drivers** - Driver information and risk scores
2. **passengers** - Passenger information
3. **rides** - Ride details and context
4. **audio_assessments** - Real-time audio risk assessments
5. **threat_indicators** - Detailed threat analysis from assessments
6. **incidents** - Full incident reports and evidence kits
7. **location_risks** - Geographic risk analysis
8. **system_logs** - Application logging and monitoring

## Setup Instructions

### Prerequisites

1. **Conda Environment**
   ```bash
   # Install conda if not already installed
   brew install miniconda
   conda init zsh
   source ~/.zshrc
   ```

2. **Alibaba Cloud ApsaraDB PostgreSQL**
   - Create a PostgreSQL instance in Alibaba Cloud
   - Note down the connection details

### Quick Setup with Conda

```bash
# 1. Setup conda environment and dependencies
make conda-setup

# 2. Activate the environment
conda activate ai-service

# 3. Configure your database connection
cp .env.example .env
# Edit .env with your database credentials

# 4. Initialize the database
make conda-init-db

# 5. Run the application
make conda-run
```

### Manual Setup

```bash
# 1. Create conda environment
conda create -n ai-service python=3.11 -y
conda activate ai-service

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment variables
cp .env.example .env
# Edit .env file with your configuration

# 4. Initialize database
python init_db.py

# 5. Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Configuration

Create a `.env` file with your Alibaba Cloud credentials:

```env
# Alibaba Cloud Configuration
ALIBABA_ACCESS_KEY_ID=your_access_key_id
ALIBABA_ACCESS_KEY_SECRET=your_access_key_secret
ALIBABA_REGION=ap-southeast-1
ALIBABA_APPKEY=your_app_key

# Qwen LLM Configuration
DASHSCOPE_API_KEY=your_dashscope_api_key

# ApsaraDB PostgreSQL Configuration
DATABASE_HOST=your-apsaradb-host.polardb.singapore.rds.aliyuncs.com
DATABASE_PORT=5432
DATABASE_NAME=ai_service_db
DATABASE_USER=your_username
DATABASE_PASSWORD=your_password
DATABASE_SSL_MODE=require

# Application Settings
DEBUG=false
LOW_RISK_THRESHOLD=39
MEDIUM_RISK_THRESHOLD=69
MAX_AUDIO_SIZE_MB=50
```

## Database Schema Details

### Audio Assessments Table
Stores real-time audio risk assessments from the `/api/assessment` endpoint.

```sql
CREATE TABLE audio_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id VARCHAR(100) UNIQUE NOT NULL,
    driver_id VARCHAR(100) NOT NULL,
    ride_id VARCHAR(100),
    audio_file_path VARCHAR(500),
    audio_duration_seconds FLOAT,
    location_lat FLOAT,
    location_lng FLOAT,
    transcribed_text TEXT,
    risk_score FLOAT NOT NULL,
    risk_level risk_level_enum NOT NULL,
    threat_text_score FLOAT,
    location_risk_index FLOAT,
    driver_history_score FLOAT,
    action_required BOOLEAN DEFAULT FALSE,
    push_notification TEXT,
    processing_timestamp TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Incidents Table
Stores comprehensive incident reports from the `/api/summarize` endpoint.

```sql
CREATE TABLE incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id VARCHAR(100) UNIQUE NOT NULL,
    evidence_kit_id VARCHAR(100) UNIQUE NOT NULL,
    driver_id VARCHAR(100) NOT NULL,
    ride_id VARCHAR(100),
    passenger_id VARCHAR(100),
    audio_file_path VARCHAR(500),
    full_transcript TEXT,
    primary_category VARCHAR(100) NOT NULL,
    secondary_categories JSON,
    severity_level incident_severity_enum NOT NULL,
    urgency incident_urgency_enum NOT NULL,
    executive_summary TEXT NOT NULL,
    risk_assessment JSON,
    recommended_actions JSON,
    overall_risk_score FLOAT NOT NULL,
    confidence_level FLOAT NOT NULL,
    status VARCHAR(50) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Drivers Table
Tracks driver information and risk history.

```sql
CREATE TABLE drivers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    driver_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255),
    risk_history_score FLOAT DEFAULT 0.0,
    total_rides INTEGER DEFAULT 0,
    incident_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## API Endpoints

### Assessment Endpoints
- `POST /api/assessment` - Real-time audio risk assessment
- `GET /api/db/assessment/{assessment_id}` - Get assessment details
- `GET /api/db/assessments/recent` - Get recent high-risk assessments

### Evidence Kit Endpoints
- `POST /api/summarize` - Create comprehensive incident evidence kit

### Database Management
- `GET /health` - Application and database health check
- `GET /api/db/health/database` - Database-specific health check
- `GET /api/db/driver/{driver_id}/risk` - Get driver risk score
- `GET /api/db/location/risk` - Get location risk index

## Monitoring and Logging

The system includes comprehensive logging:

```python
# System logs are automatically stored
await db_service.log_system_event(
    level="INFO",
    service="assessment_api",
    message="Assessment completed",
    context={"assessment_id": "...", "risk_level": "HIGH"}
)
```

Access logs via:
- Database table: `system_logs`
- Application logs: Check console output

## Database Migrations

For future schema changes, use Alembic:

```bash
# Initialize migrations (first time only)
conda activate ai-service
alembic init alembic

# Create a new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head
```

## Security Considerations

1. **SSL/TLS**: Always use SSL connections to ApsaraDB
2. **Network Security**: Configure VPC and security groups
3. **Access Control**: Use IAM roles and database users with minimal privileges
4. **Data Encryption**: Enable encryption at rest in ApsaraDB
5. **Backup**: Configure automated backups

## Performance Optimization

1. **Connection Pooling**: Configured in `database.py`
2. **Indexing**: Key fields are indexed for performance
3. **Async Operations**: All database operations are asynchronous
4. **Query Optimization**: Use repository pattern for efficient queries

## Troubleshooting

### Common Issues

1. **Connection Failed**
   ```bash
   # Check database credentials in .env
   # Verify network connectivity
   # Check security group settings
   ```

2. **Import Errors**
   ```bash
   # Ensure conda environment is activated
   conda activate ai-service
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

3. **Database Tables Not Created**
   ```bash
   # Reinitialize database
   python init_db.py
   ```

### Logs and Debugging

```bash
# Check application logs
tail -f logs/app.log

# Check database connectivity
python -c "from app.database.database import check_database_health; import asyncio; print(asyncio.run(check_database_health()))"
```

## Support

For issues with:
- **Alibaba Cloud**: Check Alibaba Cloud documentation
- **Database Schema**: Review `app/database/models.py`
- **API Integration**: Check `app/main.py` and `app/api/`
- **Conda Environment**: Run `conda info` and `conda list`

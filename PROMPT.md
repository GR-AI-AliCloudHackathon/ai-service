# GoShield – Real-Time Ride-Safety Pipeline (MVP)
**Hackathon prototype for protecting women & children on ride-sharing platforms, built entirely on Alibaba Cloud, especially for GoTo aka Gojek Tokopedia company**

---

## 🎯 Project Overview
GoShield adalah intelligent safety monitoring system yang menyediakan real-time protection untuk vulnerable passengers selama ride-sharing trips. System ini memanfaatkan AI capabilities untuk detect potential threats melalui audio analysis, location tracking, dan driver behavior assessment.

---

## ✨ Core Features (MVP)

### 🛡️ **Real-Time Safety Monitoring**
- **Activation**: Passenger taps GoShield panic button untuk start monitoring
- **Audio Processing**: Continuous 10-second audio slice recording dan analysis
- **Multi-Factor Risk Assessment**: Combines speech analysis, location data, dan driver history
- **Intelligent Classification**: Automated threat response berdasarkan risk severity levels

### 📊 **Smart Risk Scoring System**
System menghitung risk scores menggunakan weighted algorithm:
```
Total Risk Score = (Threat Score × 0.6) + (Location Risk × 0.3) + (Driver History × 0.1)
```

---

## 🏗️ Service Architecture (MVP)

### 🔍 **Service 1: Risk Assessment Engine**
**Purpose**: Real-time threat detection dan risk scoring
- Analyze transcribed audio untuk threatening language patterns
- Evaluate location deviation dari expected route
- Incorporate driver behavioral history (dummy: 0=good, 1=bad)
- Output structured risk assessments dengan confidence scores
- Return risk classification: Low (0-39), Medium (40-69), High (≥70)

### 📝 **Service 2: Incident Summarizer**
**Purpose**: Generate incident documentation dan reporting
- Generate comprehensive incident summaries dari audio transcripts
- Create timeline-based event reports dengan key timestamps
- Produce structured incident reports untuk user access
- Save incident reports ke ApsaraDB PostgreSQL
- Provide API untuk retrieve incident history

### 🎤 **Service 3: Audio Processing Service**
**Purpose**: Handle audio recording dan transcription pipeline
- Receive 10-second audio slices dari frontend
- Upload raw audio files ke Alibaba OSS dengan organized naming
- Send audio ke Alibaba ISI untuk speech-to-text conversion
- Return transcribed text ke Risk Assessment Engine
- Handle audio processing errors dan retries

### 📊 **Service 4: Data Management Service**
**Purpose**: Handle database operations dan data persistence
- Manage incident reports di ApsaraDB PostgreSQL
- Store risk assessment results dengan metadata
- Handle user session data dan trip information
- Provide CRUD operations untuk all data entities
- Handle database connections dan transaction management

---

## 🔄 System Workflow (MVP)

### **Phase 1: Activation & Setup**
1. **User Activation**: Passenger taps GoShield button
2. **Session Initialization**: Data Management Service creates monitoring session
3. **Audio Stream Start**: Frontend mulai recording 10-second slices

### **Phase 2: Real-Time Processing**
4. **Audio Upload**: Audio Processing Service receive slice dari frontend
5. **Storage**: Audio file disimpan ke Alibaba OSS
6. **Transcription**: Audio dikirim ke Alibaba ISI untuk conversion
7. **Risk Analysis**: Risk Assessment Engine analyze transcript
8. **Location Check**: Calculate location risk index (dummy implementation)
9. **Final Scoring**: Combine all risk factors untuk total score
10. **Classification**: Assign risk level dan return ke frontend

### **Phase 3: Response & Documentation**
11. **Frontend Action**: Frontend handle notifications berdasarkan risk level:

| Risk Score | Label | Backend Action | Frontend Action (Hardcoded) |
|------------|-------|----------------|------------------------------|
| 0 – 39     | 🟢 Low   | Log event only | None |
| 40 – 69    | 🟡 Medium| Store incident | Show alert: "Medium risk detected. Confirm safety?" |
| ≥ 70       | 🔴 High  | Store incident | Show alert: "High risk detected. Confirm safety?" |

12. **Incident Creation**: For Medium/High risks, trigger Incident Summarizer
13. **Report Generation**: Summarizer creates detailed incident report
14. **Data Persistence**: Report saved ke database via Data Management Service

---

## 🏗️ Technical Stack (MVP)

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Speech-to-Text** | Alibaba Intelligent Speech Interaction (ISI) | Optimized untuk Indonesian language, low-latency |
| **AI/ML Engine** | Qwen-14B-Chat (Alibaba Model Studio) | Advanced threat detection, contextual understanding |
| **Backend Framework** | FastAPI + WebSockets | Async processing, real-time communication |
| **Audio Storage** | Alibaba Object Storage Service (OSS) | Scalable, secure audio file management |
| **Database** | ApsaraDB for PostgreSQL | Structured data storage, incident reports |
| **Deployment** | Alibaba Elastic Compute Service (ECS) | VM-based deployment dengan Makefile automation |

---

## 📊 Location Risk Index Calculation

### **Formula** (Dummy Implementation untuk MVP):
```python
def calculate_location_risk(lat, lon, expected_route, timestamp):
    # Dummy implementation - replace dengan real calculation
    import random
    base_risk = random.randint(10, 50)  # Simulate area crime rate
    
    # Simple route deviation check (dummy)
    deviation_risk = random.randint(0, 30)  # Simulate route deviation
    
    # Time factor (higher risk at night)
    hour = datetime.fromtimestamp(timestamp).hour
    time_risk = 20 if 22 <= hour or hour <= 5 else 5
    
    return min(base_risk + deviation_risk + time_risk, 100)
```

### **Real Implementation Approach**:
- **Crime Rate**: Historical crime data untuk current area (dari government data)
- **Route Deviation**: Calculate distance dari expected route menggunakan haversine formula
- **Time Factor**: Hour-of-day risk multiplier (higher pada night hours)
- **Area Type**: Location classification (residential=low, industrial=high)

---

## 📁 Folder Structure

```
goshield-backend/
├── README.md
├── Makefile                          # Deployment automation
├── docker-compose.yml               # Container orchestration
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── .gitignore
│
├── app/                             # Main application
│   ├── __init__.py
│   ├── main.py                      # FastAPI app entry point
│   ├── config.py                    # Configuration management
│   └── dependencies.py              # Shared dependencies
│
├── services/                        # Core services
│   ├── __init__.py
│   ├── risk_assessment/             # Service 1: Risk Assessment Engine
│   │   ├── __init__.py
│   │   ├── service.py               # Main service logic
│   │   ├── models.py                # Pydantic models
│   │   ├── utils.py                 # Helper functions
│   │   └── prompts.py               # LLM prompts
│   │
│   ├── incident_summarizer/         # Service 2: Incident Summarizer
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── models.py
│   │   ├── templates.py             # Summary templates
│   │   └── utils.py
│   │
│   ├── audio_processing/            # Service 3: Audio Processing
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── models.py
│   │   ├── oss_client.py            # OSS operations
│   │   └── transcription.py         # ISI integration
│   │
│   └── data_management/             # Service 4: Data Management
│       ├── __init__.py
│       ├── service.py
│       ├── models.py                # SQLAlchemy models
│       ├── database.py              # DB connection
│       └── crud.py                  # CRUD operations
│
├── api/                             # API routes
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── routes.py                # Main routes
│   │   ├── audio.py                 # Audio endpoints
│   │   ├── incidents.py             # Incident endpoints
│   │   └── health.py                # Health check
│   │
│   └── websockets/                  # WebSocket handlers
│       ├── __init__.py
│       └── monitoring.py            # Real-time monitoring
│
├── core/                            # Core utilities
│   ├── __init__.py
│   ├── security.py                  # Authentication
│   ├── logging.py                   # Logging configuration
│   ├── exceptions.py                # Custom exceptions
│   └── middleware.py                # Custom middleware
│
├── external/                        # External service clients
│   ├── __init__.py
│   ├── alibaba_isi.py               # Speech-to-text client
│   ├── qwen_client.py               # LLM client
│   └── oss_client.py                # Object storage client
│
├── database/                        # Database related
│   ├── __init__.py
│   ├── migrations/                  # Alembic migrations
│   └── schemas.sql                  # Initial schema
│
├── tests/                           # Test files
│   ├── __init__.py
│   ├── conftest.py                  # Test configuration
│   ├── unit/                        # Unit tests
│   │   ├── test_risk_assessment.py
│   │   ├── test_summarizer.py
│   │   ├── test_audio_processing.py
│   │   └── test_data_management.py
│   │
│   └── integration/                 # Integration tests
│       ├── test_api.py
│       └── test_workflows.py
│
├── scripts/                         # Utility scripts
│   ├── setup_database.py           # Database initialization
│   ├── deploy.sh                    # Deployment script
│   └── health_check.py              # System health check
│
├── docker/                          # Docker configurations
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   └── docker-entrypoint.sh
│
└── docs/                            # Documentation
    ├── api.md                       # API documentation
    ├── deployment.md                # Deployment guide
    └── architecture.md              # System architecture
```

---

## 🚀 Step-by-Step Implementation (MVP)

### **Step 1: Environment Setup**
```bash
# Clone and setup project
git clone <repo-url>
cd goshield-backend
cp .env.example .env
# Edit .env dengan Alibaba Cloud credentials
```

### **Step 2: Database Setup**
```bash
make setup-database        # Initialize PostgreSQL
make run-migrations        # Apply database schema
```

### **Step 3: External Services Configuration**
- Setup Alibaba ISI credentials
- Configure Qwen-14B-Chat access
- Create OSS bucket untuk audio storage
- Test external service connections

### **Step 4: Core Services Development**
- Implement Audio Processing Service (OSS + ISI integration)
- Build Risk Assessment Engine (Qwen integration)
- Create Data Management Service (PostgreSQL operations)
- Develop Incident Summarizer (report generation)

### **Step 5: API Development**
- Build REST API endpoints
- Implement WebSocket untuk real-time communication
- Add authentication dan session management
- Create health check endpoints

### **Step 6: Testing & Integration**
```bash
make test                  # Run unit tests
make integration-test      # Run integration tests
make load-test            # Basic load testing
```

### **Step 7: Deployment**
```bash
make build                # Build Docker images
make deploy               # Deploy to ECS
make health-check         # Verify deployment
```

---

## 🔧 Makefile Commands

```makefile
# Development
setup:               # Install dependencies
dev:                 # Run development server
test:                # Run all tests
lint:                # Code linting

# Database
setup-database:      # Initialize database
run-migrations:      # Apply migrations
seed-data:          # Load sample data

# Deployment
build:              # Build Docker images
deploy:             # Deploy to production
health-check:       # System health verification
logs:               # View application logs

# Utilities
clean:              # Clean temporary files
backup-db:          # Backup database
restore-db:         # Restore database
```

---

## 📈 Success Metrics (MVP)

- **Response Time**: < 3 seconds untuk risk assessment
- **Accuracy**: > 90% threat classification untuk obvious cases
- **Availability**: 99% system uptime
- **Throughput**: Support 100+ concurrent audio processing

---

## 🎯 MVP Scope Limitations

1. **Hardcoded Frontend**: Notifications handled di frontend (no notification service)
2. **Dummy Data**: Location risk dan driver history menggunakan dummy values
3. **Basic Security**: Minimal authentication untuk hackathon demo
4. **Single Language**: Indonesian language focus only
5. **Limited Scalability**: Optimized untuk demo, bukan production scale

---

## 🔮 Post-MVP Enhancements

- Real location risk calculation dengan crime data
- Advanced driver scoring algorithm
- Dedicated notification service
- Multi-language support
- Production-grade security dan monitoring
# Database initialization script
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import init_database, engine
from app.database.models import Base
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_tables():
    """Create all database tables"""
    try:
        logger.info("Creating database tables...")
        await init_database()
        logger.info("✅ Database tables created successfully!")
        
        # Print table information
        async with engine.begin() as conn:
            result = await conn.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = result.fetchall()
            
            logger.info(f"Created {len(tables)} tables:")
            for table in tables:
                logger.info(f"  - {table[0]}")
                
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        raise
    finally:
        await engine.dispose()

async def seed_initial_data():
    """Seed database with initial data"""
    from app.database.database import get_db_session
    from app.database.repositories import RepositoryManager
    from app.database.models import RiskLevelEnum, IncidentSeverityEnum, IncidentUrgencyEnum
    
    try:
        logger.info("Seeding initial data...")
        
        async with get_db_session() as session:
            repo = RepositoryManager(session)
            
            # Create some sample location risks for major areas
            sample_locations = [
                {"latitude": 1.3521, "longitude": 103.8198, "risk_index": 0.3, "location_name": "Singapore CBD"},
                {"latitude": 1.2966, "longitude": 103.7764, "risk_index": 0.2, "location_name": "Jurong"},
                {"latitude": 1.3048, "longitude": 103.8318, "risk_index": 0.4, "location_name": "Marina Bay"},
            ]
            
            for location_data in sample_locations:
                existing = await repo.locations.get_location_risk(
                    location_data["latitude"], 
                    location_data["longitude"]
                )
                if not existing:
                    from app.database.models import LocationRisk
                    location = LocationRisk(**location_data)
                    session.add(location)
            
            # Log the initialization
            await repo.logs.log(
                level="INFO",
                service="database_init",
                message="Database initialized with sample data",
                context={"tables_created": True, "sample_data": True}
            )
            
        logger.info("✅ Initial data seeded successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error seeding data: {e}")
        raise

async def main():
    """Main initialization function"""
    logger.info("🚀 Starting database initialization...")
    logger.info(f"Database URL: {settings.database_url}")
    
    try:
        # Create tables
        await create_tables()
        
        # Seed initial data
        await seed_initial_data()
        
        logger.info("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

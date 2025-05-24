#!/usr/bin/env python
# db_manager.py - Database management utility for AI Service

import argparse
import asyncio
import logging
from pathlib import Path
import sys

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database.database import init_database, check_database_health, close_database
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("db_manager")

async def check_health():
    """Check database connectivity and health"""
    logger.info("Checking database health...")
    try:
        is_healthy = await check_database_health()
        if is_healthy:
            logger.info("✅ Database connection healthy")
            logger.info(f"Connected to: {settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}")
            return True
        else:
            logger.error("❌ Database connection failed")
            return False
    except Exception as e:
        logger.error(f"❌ Error checking database health: {e}")
        return False

async def initialize_db():
    """Initialize database schema"""
    logger.info("Initializing database schema...")
    try:
        await init_database()
        logger.info("✅ Database schema initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        return False

async def setup_test_data():
    """Set up test data for development"""
    from app.database.database import get_db_session
    from app.database.repositories import RepositoryManager
    
    logger.info("Setting up test data...")
    try:
        async with get_db_session() as session:
            repo = RepositoryManager(session)
            
            # Create test drivers
            test_drivers = [
                {"driver_id": "good_driver", "name": "Safe Driver", "risk_history_score": 0.1},
                {"driver_id": "avg_driver", "name": "Average Driver", "risk_history_score": 0.5},
                {"driver_id": "bad_driver", "name": "Risky Driver", "risk_history_score": 0.8},
            ]
            
            for driver_data in test_drivers:
                existing = await repo.drivers.get_driver_by_id(driver_data["driver_id"])
                if not existing:
                    await repo.drivers.create_driver(driver_data)
                    logger.info(f"Created test driver: {driver_data['driver_id']}")
                else:
                    logger.info(f"Test driver exists: {driver_data['driver_id']}")
            
            # Create test location risks
            test_locations = [
                {"latitude": 1.3521, "longitude": 103.8198, "risk_index": 0.3, "location_name": "Singapore CBD"},
                {"latitude": 1.2966, "longitude": 103.7764, "risk_index": 0.2, "location_name": "Jurong"},
                {"latitude": 1.3048, "longitude": 103.8318, "risk_index": 0.4, "location_name": "Marina Bay"},
            ]
            
            for location_data in test_locations:
                existing = await repo.locations.get_location_risk(
                    location_data["latitude"], 
                    location_data["longitude"]
                )
                if not existing:
                    from app.database.models import LocationRisk
                    location = LocationRisk(**location_data)
                    session.add(location)
                    logger.info(f"Created test location: {location_data['location_name']}")
                else:
                    logger.info(f"Test location exists: {location_data['location_name']}")
            
        logger.info("✅ Test data setup completed")
        return True
    except Exception as e:
        logger.error(f"❌ Error setting up test data: {e}")
        return False

async def purge_db():
    """Purge all data from the database - Use with caution!"""
    from app.database.database import get_db_session
    from app.database.models import Base
    from sqlalchemy import text
    
    logger.warning("⚠️ PURGING ALL DATA FROM DATABASE!")
    logger.warning("This will delete all tables and data.")
    
    confirm = input("Type 'YES' to confirm: ")
    if confirm != "YES":
        logger.info("Operation cancelled.")
        return
    
    try:
        async with get_db_session() as session:
            # Drop all tables
            async with session.bind.begin() as conn:
                tables = await conn.run_sync(lambda sync_conn: Base.metadata.tables.keys())
                for table in tables:
                    await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
            
        logger.info("✅ Database purged successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error purging database: {e}")
        return False

async def main():
    parser = argparse.ArgumentParser(description='AI Service Database Manager')
    parser.add_argument('action', choices=[
        'health', 'init', 'test-data', 'purge'
    ], help='Action to perform')
    
    args = parser.parse_args()
    
    logger.info(f"🛠️ Database URL: {settings.database_url}")
    
    if args.action == 'health':
        await check_health()
    elif args.action == 'init':
        is_healthy = await check_health()
        if is_healthy:
            await initialize_db()
    elif args.action == 'test-data':
        is_healthy = await check_health()
        if is_healthy:
            await setup_test_data()
    elif args.action == 'purge':
        is_healthy = await check_health()
        if is_healthy:
            await purge_db()
    
    await close_database()

if __name__ == "__main__":
    asyncio.run(main())

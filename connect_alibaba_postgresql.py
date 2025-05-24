#!/usr/bin/env python
# connect_alibaba_postgresql.py - Alibaba ApsaraDB PostgreSQL connection utility

import os
import sys
import asyncio
import logging
import argparse
import getpass
import json
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("alibaba-db-connect")

async def test_connection_details():
    """Test detailed connection to the database"""
    try:
        from app.database.database import engine
        from sqlalchemy import text
        
        # Print Alibaba ApsaraDB PostgreSQL information
        logger.info("Testing connection to Alibaba ApsaraDB PostgreSQL...")
        
        connection_results = {}
        
        async with engine.begin() as conn:
            # Version information
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            connection_results["version"] = version
            logger.info(f"PostgreSQL version: {version}")
            
            # Connection limits
            result = await conn.execute(text("SHOW max_connections;"))
            max_connections = result.scalar()
            connection_results["max_connections"] = max_connections
            
            # Current connections
            result = await conn.execute(text("""
                SELECT count(*) FROM pg_stat_activity 
                WHERE datname = current_database();
            """))
            active_connections = result.scalar()
            connection_results["active_connections"] = active_connections
            
            logger.info(f"Connection limits: {active_connections} active / {max_connections} max")
            
            # Database size
            result = await conn.execute(text("""
                SELECT pg_size_pretty(pg_database_size(current_database()));
            """))
            db_size = result.scalar()
            connection_results["database_size"] = db_size
            logger.info(f"Database size: {db_size}")
            
            # Table information
            result = await conn.execute(text("""
                SELECT 
                    tablename, 
                    pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) as size
                FROM 
                    pg_tables 
                WHERE 
                    schemaname = 'public'
                ORDER BY 
                    pg_total_relation_size(schemaname || '.' || tablename) DESC;
            """))
            tables = result.fetchall()
            table_info = []
            
            if tables:
                logger.info("\nDatabase tables:")
                for table in tables:
                    logger.info(f"  - {table[0]}: {table[1]}")
                    table_info.append({"name": table[0], "size": table[1]})
            else:
                logger.info("No tables found in the database.")
                
            connection_results["tables"] = table_info
            
            # Alibaba ApsaraDB specific information (if available)
            try:
                result = await conn.execute(text("""
                    SELECT name, setting FROM pg_settings 
                    WHERE name IN ('listen_addresses', 'max_connections', 'shared_buffers', 
                                 'effective_cache_size', 'work_mem', 'maintenance_work_mem');
                """))
                settings = result.fetchall()
                
                if settings:
                    logger.info("\nDatabase settings:")
                    pg_settings = {}
                    for setting in settings:
                        logger.info(f"  - {setting[0]}: {setting[1]}")
                        pg_settings[setting[0]] = setting[1]
                    
                    connection_results["pg_settings"] = pg_settings
            except Exception as e:
                logger.warning(f"Could not retrieve PostgreSQL settings: {e}")
            
            return connection_results
            
    except Exception as e:
        logger.error(f"Error testing database connection: {e}")
        return None

async def initialize_database_tables():
    """Initialize database tables"""
    try:
        from app.database.database import init_database
        
        logger.info("Initializing database tables...")
        await init_database()
        logger.info("✅ Tables initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing database tables: {e}")
        return False

async def create_sample_data():
    """Create sample data for testing"""
    try:
        from app.database.database import get_db_session
        from app.database.repositories import RepositoryManager
        
        logger.info("Creating sample data...")
        
        async with get_db_session() as session:
            repo = RepositoryManager(session)
            
            # Create test drivers
            test_drivers = [
                {"driver_id": "test_driver_1", "name": "John Doe", "risk_history_score": 0.1, "vehicle_id": "SG12345A"},
                {"driver_id": "test_driver_2", "name": "Jane Smith", "risk_history_score": 0.4, "vehicle_id": "SG54321B"},
                {"driver_id": "test_driver_3", "name": "Bob Chen", "risk_history_score": 0.7, "vehicle_id": "SG98765C"},
            ]
            
            created_drivers = []
            for driver_data in test_drivers:
                existing = await repo.drivers.get_driver_by_id(driver_data["driver_id"])
                if not existing:
                    driver = await repo.drivers.create_driver(driver_data)
                    logger.info(f"Created test driver: {driver_data['name']}")
                    created_drivers.append(driver_data)
                else:
                    logger.info(f"Driver already exists: {driver_data['name']}")
            
            # Create test passengers
            test_passengers = [
                {"passenger_id": "test_passenger_1", "name": "Alice Wong", "account_status": "active"},
                {"passenger_id": "test_passenger_2", "name": "Michael Tan", "account_status": "active"},
            ]
            
            created_passengers = []
            for passenger_data in test_passengers:
                existing = await repo.passengers.get_passenger_by_id(passenger_data["passenger_id"])
                if not existing:
                    passenger = await repo.passengers.create_passenger(passenger_data)
                    logger.info(f"Created test passenger: {passenger_data['name']}")
                    created_passengers.append(passenger_data)
                else:
                    logger.info(f"Passenger already exists: {passenger_data['name']}")
            
            # Create test rides
            if created_drivers and created_passengers:
                test_rides = [
                    {
                        "ride_id": "test_ride_1",
                        "driver_id": created_drivers[0]["driver_id"],
                        "passenger_id": created_passengers[0]["passenger_id"],
                        "start_location": "Changi Airport",
                        "end_location": "Marina Bay Sands",
                        "start_lat": 1.3644, 
                        "start_lng": 103.9915,
                        "end_lat": 1.2838,
                        "end_lng": 103.8591,
                        "status": "completed"
                    },
                    {
                        "ride_id": "test_ride_2",
                        "driver_id": created_drivers[1]["driver_id"],
                        "passenger_id": created_passengers[1]["passenger_id"],
                        "start_location": "Orchard Road",
                        "end_location": "Sentosa",
                        "start_lat": 1.3036,
                        "start_lng": 103.8354,
                        "end_lat": 1.2494,
                        "end_lng": 103.8303,
                        "status": "in_progress"
                    }
                ]
                
                for ride_data in test_rides:
                    existing = await repo.rides.get_ride_by_id(ride_data["ride_id"])
                    if not existing:
                        ride = await repo.rides.create_ride(ride_data)
                        logger.info(f"Created test ride: {ride_data['ride_id']}")
                    else:
                        logger.info(f"Ride already exists: {ride_data['ride_id']}")
            
            # Create a test system log
            await repo.logs.log(
                level="INFO",
                service="db_connection_test",
                message="Sample data creation completed",
                context={"timestamp": "now", "status": "success"}
            )
            
            logger.info("✅ Sample data created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        return False

async def main():
    parser = argparse.ArgumentParser(description='Alibaba ApsaraDB PostgreSQL Connection Utility')
    parser.add_argument('action', choices=['test', 'init', 'sample', 'full'], 
                        help='Action to perform: test connection, initialize tables, create sample data, or do all')
    parser.add_argument('--save', action='store_true', help='Save connection details to a file')
    parser.add_argument('--output', default='db_connection_info.json', help='Output file for connection details')
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration details from environment
    from app.config import settings
    
    # Mask sensitive information
    masked_url = settings.database_url
    if settings.DATABASE_PASSWORD:
        masked_url = masked_url.replace(settings.DATABASE_PASSWORD, "*****")
    
    logger.info("=== Alibaba ApsaraDB PostgreSQL Connection Utility ===")
    logger.info(f"Database URL: {masked_url}")
    logger.info(f"Host: {settings.DATABASE_HOST}")
    logger.info(f"Database: {settings.DATABASE_NAME}")
    logger.info(f"User: {settings.DATABASE_USER}")
    
    try:
        if args.action in ['test', 'full']:
            # Test connection and get details
            connection_details = await test_connection_details()
            
            if connection_details and args.save:
                # Save to file
                output_file = args.output
                with open(output_file, 'w') as f:
                    json.dump(connection_details, f, indent=2)
                logger.info(f"Connection details saved to {output_file}")
            
            if not connection_details:
                logger.error("❌ Connection test failed")
                return 1
                
        if args.action in ['init', 'full']:
            # Initialize database tables
            if not await initialize_database_tables():
                logger.error("❌ Table initialization failed")
                return 1
        
        if args.action in ['sample', 'full']:
            # Create sample data
            if not await create_sample_data():
                logger.error("❌ Sample data creation failed")
                return 1
        
        if args.action == 'full':
            logger.info("✅ All operations completed successfully!")
        
        return 0
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    finally:
        # Close database connection
        try:
            from app.database.database import close_database
            await close_database()
        except Exception:
            pass

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

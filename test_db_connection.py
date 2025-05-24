#!/usr/bin/env python
# test_db_connection.py - Test connection to Alibaba ApsaraDB PostgreSQL

import os
import asyncio
import logging
import sys
import argparse
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.config import settings
from app.database.database import check_database_health, close_database, get_db_session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("db-connection-test")

async def test_basic_connection():
    """Test connection using the built-in health check function"""
    logger.info("\nTesting basic connection...")
    is_healthy = await check_database_health()
    
    if is_healthy:
        logger.info("✅ Basic connection successful! Database is reachable.")
    else:
        logger.error("❌ Basic connection failed. Database is not reachable.")
    
    return is_healthy

async def test_table_operations():
    """Test table operations with the database"""
    logger.info("\nTesting database operations...")
    
    try:
        async with get_db_session() as session:
            # Test query execution
            result = await session.execute(text("SELECT version();"))
            version = result.scalar()
            logger.info(f"PostgreSQL version: {version}")
            
            # Test table creation
            logger.info("Testing table creation...")
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS connection_test (
                    id SERIAL PRIMARY KEY,
                    test_timestamp TIMESTAMP DEFAULT NOW(),
                    test_data VARCHAR(255)
                )
            """))
            
            # Test data insertion
            logger.info("Testing data insertion...")
            await session.execute(
                text("INSERT INTO connection_test (test_data) VALUES (:data)"),
                {"data": "Connection test at " + str(asyncio.current_task())}
            )
            
            # Test data retrieval
            logger.info("Testing data retrieval...")
            result = await session.execute(text("SELECT COUNT(*) FROM connection_test"))
            count = result.scalar()
            logger.info(f"Connection test table has {count} rows")
            
            # Get database configuration
            result = await session.execute(text("SHOW max_connections;"))
            max_connections = result.scalar()
            
            result = await session.execute(text("SHOW shared_buffers;"))
            shared_buffers = result.scalar()
            
            logger.info(f"\nDatabase configuration:")
            logger.info(f"- Max connections: {max_connections}")
            logger.info(f"- Shared buffers: {shared_buffers}")
            
            # Test transaction commit
            await session.commit()
            logger.info("✅ Database operations completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error during database operations: {str(e)}")
        return False

async def test_custom_connection(conn_string):
    """Test connection with a custom connection string"""
    logger.info("\nTesting connection with custom string...")
    
    # Create a custom engine
    engine = create_async_engine(
        conn_string,
        echo=False,
        pool_pre_ping=True,
    )
    
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            if result.scalar() == 1:
                logger.info("✅ Custom connection successful!")
                return True
            else:
                logger.error("❌ Custom connection failed")
                return False
    except Exception as e:
        logger.error(f"❌ Custom connection error: {str(e)}")
        return False
    finally:
        await engine.dispose()

async def main():
    """Main function to test database connection"""
    parser = argparse.ArgumentParser(description="Test connection to Alibaba ApsaraDB PostgreSQL")
    parser.add_argument("--extensive", action="store_true", help="Run extensive tests including table operations")
    parser.add_argument("--custom-url", help="Test with a custom database URL")
    args = parser.parse_args()
    
    # Print configuration
    logger.info("=== Database Connection Test ===")
    
    # Mask the password in the URL
    if settings.DATABASE_PASSWORD:
        masked_url = settings.database_url.replace(settings.DATABASE_PASSWORD, "********")
    else:
        masked_url = settings.database_url
        
    logger.info(f"Database URL: {masked_url}")
    logger.info(f"Host: {settings.DATABASE_HOST}")
    logger.info(f"Port: {settings.DATABASE_PORT}")
    logger.info(f"Database: {settings.DATABASE_NAME}")
    logger.info(f"User: {settings.DATABASE_USER}")
    logger.info("Password: ********")
    logger.info(f"SSL Mode: {settings.DATABASE_SSL_MODE}")

    try:
        # Basic connection test
        basic_test_result = await test_basic_connection()
        
        # Custom URL test if provided
        if args.custom_url:
            custom_test_result = await test_custom_connection(args.custom_url)
        
        # Extensive tests
        if args.extensive and basic_test_result:
            table_test_result = await test_table_operations()
        
        # Close database connections
        await close_database()
        logger.info("\n=== Database connection test completed ===")
        
        if not basic_test_result:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Error during test execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

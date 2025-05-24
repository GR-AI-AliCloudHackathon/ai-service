#!/usr/bin/env python
# setup_database.py - Interactive database setup script

import os
import sys
import asyncio
import logging
from pathlib import Path
import getpass
import subprocess
import re

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
)
logger = logging.getLogger("setup_database")

def print_header(text):
    """Print formatted header"""
    logger.info("\n" + "=" * 60)
    logger.info(f" {text}")
    logger.info("=" * 60)

def print_step(step_num, text):
    """Print step information"""
    logger.info(f"\n[{step_num}] {text}\n")

def get_input(prompt, default=None):
    """Get input with default value"""
    if default:
        user_input = input(f"{prompt} [{default}]: ")
        return user_input if user_input else default
    return input(f"{prompt}: ")

def update_env_file(env_data):
    """Update .env file with database credentials"""
    env_path = Path(".env")
    if not env_path.exists():
        # Create from example if not exists
        example_path = Path(".env.example")
        if example_path.exists():
            env_path.write_text(example_path.read_text())
        else:
            env_path.touch()

    # Read current content
    current_content = env_path.read_text() if env_path.exists() else ""
    
    # Update or add each item
    for key, value in env_data.items():
        if re.search(rf"^{key}=.*", current_content, re.MULTILINE):
            # Update existing key
            current_content = re.sub(
                rf"^{key}=.*$", 
                f"{key}={value}", 
                current_content, 
                flags=re.MULTILINE
            )
        else:
            # Add new key
            current_content += f"\n{key}={value}"
    
    # Write updated content
    env_path.write_text(current_content)
    logger.info(f".env file updated with database configuration")

async def main():
    print_header("Alibaba ApsaraDB PostgreSQL Setup for AI Service")
    
    print_step(1, "Database Configuration")
    logger.info("Enter your Alibaba ApsaraDB PostgreSQL connection details:")
    
    db_host = get_input("Database Host (e.g., my-db.polardb.singapore.rds.aliyuncs.com)")
    db_port = get_input("Database Port", "5432")
    db_name = get_input("Database Name", "ai_service_db")
    db_user = get_input("Database Username")
    db_password = getpass.getpass("Database Password: ")
    
    # Update .env file
    env_data = {
        "DATABASE_HOST": db_host,
        "DATABASE_PORT": db_port,
        "DATABASE_NAME": db_name,
        "DATABASE_USER": db_user,
        "DATABASE_PASSWORD": db_password,
        "DATABASE_SSL_MODE": "require"
    }
    
    update_env_file(env_data)
    
    print_step(2, "Testing Database Connection")
    logger.info("Let's test the connection to your database...")
    
    # Reload settings from updated .env file
    from importlib import reload
    from app.config import settings
    reload(sys.modules['app.config'])
    from app.config import settings
    
    try:
        from app.database.database import check_database_health, close_database
        is_healthy = await check_database_health()
        
        if is_healthy:
            logger.info("✅ Connection successful! Your database is reachable.")
        else:
            logger.info("❌ Connection failed. Please check your credentials and make sure the database is accessible.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Error connecting to database: {e}")
        logger.info("Please check your credentials and make sure the database is accessible.")
        sys.exit(1)
    
    print_step(3, "Creating Database Schema")
    run_migrations = get_input("Would you like to create the database schema now? (y/n)", "y")
    
    if run_migrations.lower() == "y":
        logger.info("Running database migrations...")
        
        try:
            subprocess.run(["alembic", "upgrade", "head"], check=True)
            logger.info("✅ Database schema created successfully!")
        except subprocess.CalledProcessError:
            logger.error("❌ Failed to run migrations. Please check the output above for errors.")
            sys.exit(1)
    
    print_step(4, "Setting Up Test Data")
    setup_test_data = get_input("Would you like to set up test data? (y/n)", "y")
    
    if setup_test_data.lower() == "y":
        logger.info("Setting up test data...")
        
        try:
            from app.database.database import get_db_session
            from app.database.repositories import RepositoryManager
            
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
                        logger.info(f"Test driver already exists: {driver_data['driver_id']}")
            
            logger.info("✅ Test data setup completed!")
        except Exception as e:
            logger.error(f"❌ Error setting up test data: {e}")
    
    # Close database connections
    await close_database()
    
    print_header("Setup Complete")
    logger.info("Your database has been set up successfully!")
    logger.info("\nNext steps:")
    logger.info("1. Start the application with: make conda-run")
    logger.info("2. Access the API at: http://localhost:8000")
    logger.info("3. Check the API documentation at: http://localhost:8000/docs")

if __name__ == "__main__":
    asyncio.run(main())

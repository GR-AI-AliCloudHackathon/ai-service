# Alibaba ApsaraDB PostgreSQL Connection Guide

This guide will help you connect the application to an Alibaba ApsaraDB PostgreSQL instance.

## Pre-requisites

1. Access to an Alibaba Cloud account
2. An ApsaraDB PostgreSQL instance created and running
3. Network access to the database (properly configured Security Groups)
4. Conda environment for Python dependencies

## Step 1: Install Dependencies

First, ensure you have all required dependencies installed:

```bash
# Activate your conda environment
conda activate ai-service

# Install dependencies
./setup_dependencies.sh
```

## Step 2: Configure Database Connection

Create or update your `.env` file with your Alibaba ApsaraDB PostgreSQL connection details:

```bash
# Copy example file if you don't have one yet
cp .env.example .env

# Edit the .env file with your database details
```

The relevant database section in .env should look like:

```
# ApsaraDB PostgreSQL Configuration
DATABASE_HOST=your-instance-public-endpoint.polardb.singapore.rds.aliyuncs.com
DATABASE_PORT=5432
DATABASE_NAME=your_database_name
DATABASE_USER=your_username  
DATABASE_PASSWORD=your_secure_password
DATABASE_SSL_MODE=require
```

## Step 3: Test Database Connection

Test the connection to ensure everything is configured properly:

```bash
# Test the database connection
./connect_alibaba_postgresql.py test
```

If successful, you should see information about your Alibaba PostgreSQL instance including version, active connections, and any existing tables.

## Step 4: Initialize Database Schema

If you're setting up for the first time, initialize the database schema:

```bash
# Initialize database tables
./connect_alibaba_postgresql.py init
```

## Step 5: Create Sample Data (Optional)

For development purposes, you can create sample data:

```bash
# Create sample data
./connect_alibaba_postgresql.py sample
```

## Step 6: Run the Application

Start the application which will connect to your Alibaba ApsaraDB PostgreSQL:

```bash
# Using conda 
make conda-run

# Or directly with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Troubleshooting

### Connection Issues

1. **Error: "Cannot connect to host"**
   - Check if the database host is correct
   - Verify network access (security groups, firewall)
   - Try connecting with `psql` to isolate the issue

2. **Error: "Password authentication failed"**
   - Verify your username and password
   - Check if the user has proper permissions

3. **SSL Connection Issues**
   - Try different SSL modes (require, verify-ca, verify-full)
   - Check SSL certificate configuration

### Database Operations Issues

1. **Error: "Relation does not exist"**
   - Run database initialization (`./connect_alibaba_postgresql.py init`)
   - Check if alembic migrations were run correctly

2. **Performance Issues**
   - Check connection pool settings in app/database/database.py
   - Verify instance specifications in Alibaba Cloud console
   - Monitor database performance using Alibaba Cloud tools

## Alibaba Cloud Resources

- [ApsaraDB RDS for PostgreSQL Documentation](https://www.alibabacloud.com/help/product/26090.htm)
- [Connect to an ApsaraDB RDS for PostgreSQL instance](https://www.alibabacloud.com/help/doc-detail/26158.htm)
- [Alibaba Cloud Performance Monitoring](https://www.alibabacloud.com/help/doc-detail/102748.htm)

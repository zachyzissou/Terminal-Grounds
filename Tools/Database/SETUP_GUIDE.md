# PostgreSQL Setup Guide for Terminal Grounds Territorial System
## Week 1 Database Foundation Requirements

### **DIAGNOSIS: PostgreSQL Not Installed**
The territorial control system requires PostgreSQL 13+ with PostGIS spatial extensions. This is not currently installed on the development system.

---

## **OPTION A: Full Local Development Setup**

### **1. Install PostgreSQL 13+ with PostGIS**
```bash
# Download PostgreSQL installer
# URL: https://www.postgresql.org/download/windows/
# Version: PostgreSQL 13 or higher
# Include: PostGIS extension during installation
```

**Installation Steps:**
1. Download PostgreSQL Windows installer
2. Run installer as Administrator
3. **IMPORTANT**: Select PostGIS extension during component selection
4. Set password for postgres user (remember this)
5. Default port 5432 is fine
6. Complete installation

### **2. Create Terminal Grounds Database**
```bash
# Open Command Prompt as Administrator
createdb -U postgres terminal_grounds_territorial

# Run our schema setup
psql -U postgres -d terminal_grounds_territorial -f "Tools\Database\setup_territorial_database.sql"
```

### **3. Validate Installation**
```bash
# Test connection
psql -U postgres -c "SELECT version()"

# Test PostGIS
psql -U postgres -d terminal_grounds_territorial -c "SELECT PostGIS_Version()"

# Run validation script
python Tools\Database\validate_setup.py
```

---

## **OPTION B: Docker Development Environment**

### **1. Install Docker Desktop**
```bash
# Download: https://www.docker.com/products/docker-desktop
# Install Docker Desktop for Windows
```

### **2. Create PostgreSQL Container**
```bash
# Create territorial database container
docker run --name tg-territorial-db \
  -e POSTGRES_DB=terminal_grounds_territorial \
  -e POSTGRES_USER=tg_territorial \
  -e POSTGRES_PASSWORD=territorial_secure_2025 \
  -p 5432:5432 \
  -d postgis/postgis:13-3.1

# Wait for container to start
docker logs tg-territorial-db
```

### **3. Initialize Database**
```bash
# Copy schema to container
docker cp Tools\Database\setup_territorial_database.sql tg-territorial-db:/setup.sql

# Run setup script
docker exec tg-territorial-db psql -U tg_territorial -d terminal_grounds_territorial -f /setup.sql

# Validate setup
python Tools\Database\validate_setup.py
```

---

## **OPTION C: Cloud Database (Production/Team)**

### **1. PostgreSQL Cloud Services**
- **AWS RDS**: PostgreSQL with PostGIS extension
- **Google Cloud SQL**: PostgreSQL with PostGIS support  
- **Azure Database**: PostgreSQL with PostGIS extension
- **DigitalOcean**: Managed PostgreSQL with PostGIS

### **2. Setup Cloud Instance**
1. Create PostgreSQL 13+ instance with PostGIS extension
2. Configure security groups for development access
3. Note connection details (host, port, username, password)
4. Update `validate_setup.py` with connection details

### **3. Deploy Schema**
```bash
# Update connection config in validate_setup.py
db_config = {
    'host': 'your-cloud-host',
    'database': 'terminal_grounds_territorial', 
    'user': 'your_username',
    'password': 'your_password',
    'port': 5432
}

# Run deployment
python Tools\Database\validate_setup.py
```

---

## **IMMEDIATE DEVELOPMENT WORKAROUND**

Since PostgreSQL is not immediately available, let me create a **mock database validation** that allows us to continue with UE5 module testing:

### **Mock Validation (Development Only)**
```python
# Create simplified validation for immediate development
# This allows UE5 module work to proceed while database is being set up
```

**Next Steps:**
1. **Database Team**: Install PostgreSQL (Option A or B)
2. **UE5 Team**: Continue with module compilation (independent of database)
3. **Integration Team**: Combine systems once database is operational

---

## **RECOMMENDED APPROACH: Docker (Option B)**

**Why Docker?**
- Quick setup (5 minutes vs 30+ minutes for full PostgreSQL install)
- Isolated environment
- Easy to reset/recreate
- Matches production deployment patterns
- No system-wide PostgreSQL installation required

**Implementation:**
```bash
# One-time setup
docker run --name tg-territorial-db -e POSTGRES_DB=terminal_grounds_territorial -e POSTGRES_USER=tg_territorial -e POSTGRES_PASSWORD=territorial_secure_2025 -p 5432:5432 -d postgis/postgis:13-3.1

# Daily development
docker start tg-territorial-db  # Start database
# ... development work ...
docker stop tg-territorial-db   # Stop when done
```

This approach gets the territorial system operational quickly while maintaining professional database practices.
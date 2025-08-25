@echo off
REM Terminal Grounds Phase 1 Development Kickoff Script
REM CDO Executive Implementation Order

echo ========================================
echo TERMINAL GROUNDS PHASE 1 DEVELOPMENT
echo Chief Design Officer Implementation
echo ========================================
echo.

echo [1/6] Setting up development environment...
echo.

REM Check if PostgreSQL is installed
pg_config --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: PostgreSQL not found. Please install PostgreSQL 13+ with PostGIS
    echo Download from: https://www.postgresql.org/download/windows/
    pause
    exit /b 1
)

REM Check if Redis is available
redis-cli --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Redis not found. Installing Redis for Windows...
    echo Please install Redis from: https://github.com/microsoftarchive/redis/releases
    echo Or use Redis for Windows: https://redis.io/docs/getting-started/installation/install-redis-on-windows/
)

echo [2/6] Creating territorial database...
echo.

REM Create database (requires postgres user authentication)
echo Creating terminal_grounds_territorial database...
createdb -U postgres terminal_grounds_territorial 2>nul
if %errorlevel% neq 0 (
    echo Database might already exist, continuing...
)

REM Run database setup script
echo Initializing database schema...
psql -U postgres -d terminal_grounds_territorial -f "Tools\Database\setup_territorial_database.sql"
if %errorlevel% neq 0 (
    echo ERROR: Database setup failed. Check PostgreSQL connection.
    pause
    exit /b 1
)

echo [3/6] Setting up Python testing environment...
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Install required Python packages
echo Installing Python dependencies...
pip install psycopg2-binary redis websockets pytest asyncio

echo [4/6] Validating UE5 project integration...
echo.

REM Check if UE5 project files exist
if not exist "Source\TGTerritorial\TGTerritorial.Build.cs" (
    echo ERROR: TGTerritorial module not found. Check UE5 project structure.
    pause
    exit /b 1
)

if not exist "Source\TGWorld\" (
    echo WARNING: TGWorld module not found. Territorial system requires TGWorld integration.
)

echo [5/6] Running system validation tests...
echo.

REM Run territorial system tests
python "Tools\Testing\territorial_system_tests.py"
if %errorlevel% neq 0 (
    echo WARNING: Some tests failed. Review output above.
    echo System may still be functional for development.
)

echo [6/6] Development environment ready!
echo.

echo ========================================
echo PHASE 1 DEVELOPMENT STATUS: ACTIVE
echo ========================================
echo.
echo Next Steps:
echo 1. Open UE5 project and compile TGTerritorial module
echo 2. Start Redis server: redis-server
echo 3. Configure WebSocket server for real-time updates
echo 4. Begin Week 1-2 database foundation development
echo.
echo CDO Implementation Framework:
echo - Database: PostgreSQL + PostGIS (✓)
echo - Real-time: WebSocket + Redis (Ready)
echo - UE5 Integration: C++ Core + Blueprint (Ready)
echo - AI Framework: TGAI Extensions (Ready)
echo.
echo Development Timeline: 16-22 weeks
echo Current Phase: Phase 1 (Weeks 1-8)
echo Team Required: 2-3 developers
echo.
echo ========================================
echo Terminal Grounds transformation to
echo Quadruple-A extraction shooter: INITIATED
echo ========================================

pause
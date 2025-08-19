@echo off
REM 🍀 OpenLucky Installation Script for Windows
REM OpenLucky Windows 一键安装脚本

echo 🍀 Welcome to OpenLucky v1.0 Installation
echo ========================================

REM Check Python version
echo 📋 Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python not found. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo ✅ Python version: %python_version%

REM Check pip
echo 📦 Checking pip availability...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: pip not found. Please install pip and try again.
    pause
    exit /b 1
)

echo ✅ pip is available

REM Install dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Error: Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

REM Create configuration file
echo ⚙️ Setting up configuration...
if not exist "config.ini" (
    copy config.ini.template config.ini
    echo ✅ Configuration template copied to config.ini
    echo 📝 Please edit config.ini and add your API keys:
    echo    - OKX API credentials (api_key, api_secret, api_passphrase)
    echo    - xAI API key
) else (
    echo ⚠️ config.ini already exists, skipping template copy
)

REM Create directories
echo 📁 Creating directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
echo ✅ Directories created

echo.
echo 🎉 Installation completed successfully!
echo.
echo 📝 Next steps:
echo 1. Edit config.ini and add your API keys
echo 2. Run: python okx_sync.py (to start data synchronization)
echo 3. Run: python main.py (to start the trading bot)
echo.
echo 📚 For detailed instructions, please read README.md
echo.
echo ⚠️ IMPORTANT: Please read the risk warnings in README.md before trading!
echo.
echo 🍀 Good luck with your trading!
echo.
pause

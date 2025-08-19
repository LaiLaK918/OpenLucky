#!/bin/bash
# 🍀 OpenLucky Installation Script
# OpenLucky 一键安装脚本

set -e  # Exit on any error

echo "🍀 Welcome to OpenLucky v1.0 Installation"
echo "========================================"

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.8+ required. Current version: $python_version"
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Check if pip is available
echo "📦 Checking pip availability..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 not found. Please install pip and try again."
    exit 1
fi

echo "✅ pip3 is available"

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

echo "✅ Dependencies installed successfully"

# Create configuration file from template
echo "⚙️ Setting up configuration..."
if [ ! -f "config.ini" ]; then
    cp config.ini.template config.ini
    echo "✅ Configuration template copied to config.ini"
    echo "📝 Please edit config.ini and add your API keys:"
    echo "   - OKX API credentials (api_key, api_secret, api_passphrase)"
    echo "   - xAI API key"
else
    echo "⚠️ config.ini already exists, skipping template copy"
fi

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data
echo "✅ Data directory created"

# Create logs directory  
echo "📄 Creating logs directory..."
mkdir -p logs
echo "✅ Logs directory created"

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Edit config.ini and add your API keys"
echo "2. Run: python okx_sync.py (to start data synchronization)"
echo "3. Run: python main.py (to start the trading bot)"
echo ""
echo "📚 For detailed instructions, please read README.md"
echo ""
echo "⚠️ IMPORTANT: Please read the risk warnings in README.md before trading!"
echo ""
echo "🍀 Good luck with your trading!"

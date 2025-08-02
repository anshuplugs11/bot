#!/usr/bin/env python3
"""
Setup Script for Weather Bot
Automates the initial setup process
"""

import os
import sys
import subprocess
import getpass
from pathlib import Path

def print_banner():
    """Print setup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🌤️  WEATHER BOT SETUP                     ║
    ║                                                              ║
    ║           Advanced Telegram Weather Bot                      ║
    ║               Multi-language Support                         ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version.split()[0]} - Compatible")

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ All packages installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages. Please check your internet connection.")
        return False
    
    return True

def create_env_file():
    """Create environment configuration file"""
    print("\n⚙️  Setting up environment configuration...")
    
    if os.path.exists('.env'):
        response = input("📄 .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("📄 Using existing .env file")
            return True
    
    print("\n🔑 Please provide the following API credentials:")
    print("   (You can always edit these later in the .env file)")
    
    # Get Telegram Bot Token
    print("\n🤖 TELEGRAM BOT TOKEN")
    print("   Get this from @BotFather on Telegram")
    print("   Visit: https://t.me/botfather")
    bot_token = getpass.getpass("   Enter your bot token: ").strip()
    
    if not bot_token:
        print("❌ Bot token is required!")
        return False
    
    # Get WeatherAPI Key
    print("\n🌤️  WEATHER API KEY")
    print("   Get a free key from WeatherAPI.com")
    print("   Visit: https://www.weatherapi.com/signup.aspx")
    weather_key = getpass.getpass("   Enter your weather API key: ").strip()
    
    if not weather_key:
        print("❌ Weather API key is required!")
        return False
    
    # Optional settings
    print("\n📋 Optional Settings (press Enter for defaults)")
    
    default_lang = input("   Default language (en): ").strip() or "en"
    temp_unit = input("   Temperature unit (celsius): ").strip() or "celsius"
    wind_unit = input("   Wind unit (kmh): ").strip() or "kmh"
    
    # Create .env file
    env_content = f"""# Telegram Bot Configuration
BOT_TOKEN={bot_token}

# Weather API Configuration  
WEATHER_API_KEY={weather_key}

# Database Configuration
DATABASE_URL=sqlite:///weather_bot.db

# Bot Settings
DEFAULT_LANGUAGE={default_lang}
TEMPERATURE_UNIT={temp_unit}
WIND_UNIT={wind_unit}

# Optional: Redis for caching
# REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10

# Logging
LOG_LEVEL=INFO
LOG_FILE=weather_bot.log

# Feature Flags
ENABLE_ANALYTICS=true
ENABLE_NOTIFICATIONS=true

# Performance
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT=30

# Geographic
DEFAULT_TIMEZONE=UTC
MAX_LOCATION_RESULTS=5

# Optional: Webhook for production
# WEBHOOK_URL=https://your-domain.com/webhook
# WEBHOOK_PORT=8443

# Optional: Admin Users (comma-separated user IDs)
# ADMIN_USER_IDS=123456789,987654321
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Environment file created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def initialize_database():
    """Initialize the database"""
    print("\n🗄️  Initializing database...")
    
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False

def test_bot_setup():
    """Test if bot setup is working"""
    print("\n🧪 Testing bot configuration...")
    
    try:
        from config import Config
        config = Config()
        print("✅ Configuration loaded successfully!")
        
        # Test weather service
        print("🌤️  Testing weather service...")
        from weather_service import WeatherService
        weather_service = WeatherService(config.WEATHER_API_KEY)
        print("✅ Weather service initialized!")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def create_systemd_service():
    """Create systemd service file for Linux"""
    if os.name != 'posix':
        return
    
    response = input("\n🐧 Create systemd service for auto-start? (y/N): ")
    if response.lower() != 'y':
        return
    
    username = input("Enter your username: ").strip()
    if not username:
        print("❌ Username required")
        return
    
    current_dir = os.getcwd()
    service_content = f"""[Unit]
Description=Weather Bot
After=network.target

[Service]
Type=simple
User={username}
WorkingDirectory={current_dir}
ExecStart={sys.executable} {current_dir}/main.py
Restart=always
RestartSec=10
Environment=PYTHONPATH={current_dir}

[Install]
WantedBy=multi-user.target
"""
    
    service_file = f"{current_dir}/weather-bot.service"
    try:
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        print(f"✅ Service file created: {service_file}")
        print("\n📋 To install the service:")
        print(f"   sudo cp {service_file} /etc/systemd/system/")
        print("   sudo systemctl daemon-reload")
        print("   sudo systemctl enable weather-bot.service")
        print("   sudo systemctl start weather-bot.service")
        
    except Exception as e:
        print(f"❌ Failed to create service file: {e}")

def show_completion_message():
    """Show setup completion message"""
    completion_msg = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🎉 SETUP COMPLETE!                        ║
    ╠══════════════════════════════════════════════════════════════╣
    ║                                                              ║
    ║  Your Weather Bot is ready to use!                          ║
    ║                                                              ║
    ║  🚀 To start the bot:                                        ║
    ║     python main.py                                           ║
    ║                                                              ║
    ║  📚 Next steps:                                              ║
    ║     • Test your bot by messaging it on Telegram             ║
    ║     • Add your bot to groups (optional)                     ║
    ║     • Check logs in weather_bot.log                         ║
    ║     • Customize settings in .env file                       ║
    ║                                                              ║
    ║  🆘 Need help?                                               ║
    ║     • Read README.md for detailed documentation             ║
    ║     • Check troubleshooting section                         ║
    ║     • Create an issue on GitHub                             ║
    ║                                                              ║
    ║  🌟 Enjoy your weather bot!                                 ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(completion_msg)

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    check_python_version()
    
    # Check if all files exist
    required_files = ['main.py', 'requirements.txt', 'weather_service.py', 'config.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("   Please ensure you have all bot files in the current directory.")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Create environment file
    if not create_env_file():
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        sys.exit(1)
    
    # Test configuration
    if not test_bot_setup():
        print("\n⚠️  Configuration issues detected.")
        print("   Please check your API keys and try again.")
        response = input("   Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Optional: Create systemd service
    create_systemd_service()
    
    # Show completion message
    show_completion_message()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        sys.exit(1)

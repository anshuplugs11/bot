#!/usr/bin/env python3
"""
Configuration Module
Contains all configuration settings and environment variables
"""

import os
from typing import Optional

class Config:
    def __init__(self):
        # Bot Configuration
        self.BOT_TOKEN = os.getenv('BOT_TOKEN')
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        # Weather API Configuration
        self.WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
        if not self.WEATHER_API_KEY:
            # You can get a free API key from https://www.weatherapi.com/
            raise ValueError("WEATHER_API_KEY environment variable is required")
        
        # Database Configuration
        self.DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///weather_bot.db')
        
        # Redis Configuration (for caching - optional)
        self.REDIS_URL = os.getenv('REDIS_URL')
        self.CACHE_TTL = int(os.getenv('CACHE_TTL', '300'))  # 5 minutes default
        
        # Rate Limiting
        self.RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '10'))
        
        # Logging Configuration
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', 'weather_bot.log')
        
        # Bot Settings
        self.DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'en')
        self.TEMPERATURE_UNIT = os.getenv('TEMPERATURE_UNIT', 'celsius')  # celsius or fahrenheit
        self.WIND_UNIT = os.getenv('WIND_UNIT', 'kmh')  # kmh or mph
        
        # Feature Flags
        self.ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'true').lower() == 'true'
        self.ENABLE_NOTIFICATIONS = os.getenv('ENABLE_NOTIFICATIONS', 'true').lower() == 'true'
        
        # Webhook Configuration (for production)
        self.WEBHOOK_URL = os.getenv('WEBHOOK_URL')
        self.WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '8443'))
        
        # Admin Settings
        self.ADMIN_USER_IDS = [
            int(uid) for uid in os.getenv('ADMIN_USER_IDS', '').split(',') 
            if uid.strip().isdigit()
        ]
        
        # Performance Settings
        self.MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', '100'))
        self.REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
        
        # Geographic Settings
        self.DEFAULT_TIMEZONE = os.getenv('DEFAULT_TIMEZONE', 'UTC')
        self.MAX_LOCATION_RESULTS = int(os.getenv('MAX_LOCATION_RESULTS', '5'))
    
    def get_database_config(self) -> dict:
        """Get database configuration dictionary"""
        return {
            'url': self.DATABASE_URL,
            'echo': self.LOG_LEVEL.upper() == 'DEBUG'
        }
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.ADMIN_USER_IDS
    
    def get_api_endpoints(self) -> dict:
        """Get API endpoints configuration"""
        return {
            'weather_api': 'http://api.weatherapi.com/v1',
            'backup_api': 'https://api.openweathermap.org/data/2.5'  # Backup API
        }

# Environment file template for easy setup
ENV_TEMPLATE = """
# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here

# Weather API Configuration  
WEATHER_API_KEY=your_weatherapi_key_here

# Database Configuration
DATABASE_URL=sqlite:///weather_bot.db

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10

# Logging
LOG_LEVEL=INFO
LOG_FILE=weather_bot.log

# Bot Settings
DEFAULT_LANGUAGE=en
TEMPERATURE_UNIT=celsius
WIND_UNIT=kmh

# Feature Flags
ENABLE_ANALYTICS=true
ENABLE_NOTIFICATIONS=true

# Webhook (for production deployment)
WEBHOOK_URL=https://your-domain.com/webhook
WEBHOOK_PORT=8443

# Admin Users (comma-separated user IDs)
ADMIN_USER_IDS=123456789,987654321

# Performance
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT=30

# Geographic
DEFAULT_TIMEZONE=UTC
MAX_LOCATION_RESULTS=5
"""

def create_env_file():
    """Create a sample .env file"""
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(ENV_TEMPLATE.strip())
        print("Created .env file template. Please fill in your API keys.")
    else:
        print(".env file already exists.")

if __name__ == "__main__":
    create_env_file()

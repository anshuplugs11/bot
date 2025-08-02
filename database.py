#!/usr/bin/env python3
"""
Database Module
Handles all database operations for user preferences and analytics
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import threading

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = 'weather_bot.db'):
        self.db_path = db_path
        self.local = threading.local()
        self._init_database()
    
    def _get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self.local, 'connection'):
            self.local.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.local.connection.row_factory = sqlite3.Row
        return self.local.connection
    
    def _init_database(self):
        """Initialize database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language_code TEXT DEFAULT 'en',
                default_location TEXT,
                temperature_unit TEXT DEFAULT 'celsius',
                wind_unit TEXT DEFAULT 'kmh',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                notification_enabled BOOLEAN DEFAULT 1
            )
        ''')
        
        # User locations table for favorites
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                location_name TEXT,
                latitude REAL,
                longitude REAL,
                is_default BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Weather requests log for analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                location TEXT,
                request_type TEXT,
                response_time REAL,
                success BOOLEAN,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # User sessions for analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_start TIMESTAMP,
                session_end TIMESTAMP,
                requests_count INTEGER DEFAULT 0,
                locations_queried TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Weather alerts subscriptions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                location TEXT,
                latitude REAL,
                longitude REAL,
                alert_types TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Cache table for weather data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_key TEXT UNIQUE,
                data_type TEXT,
                weather_data TEXT,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully")
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, 
                 last_name: str = None, language_code: str = 'en') -> bool:
        """Add new user or update existing user"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, last_name, language_code, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, language_code, datetime.now()))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def set_user_language(self, user_id: int, language_code: str) -> bool:
        """Set user's preferred language"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET language_code = ?, updated_at = ?
                WHERE user_id = ?
            ''', (language_code, datetime.now(), user_id))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error setting user language: {e}")
            return False
    
    def get_user_language(self, user_id: int) -> Optional[str]:
        """Get user's preferred language"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT language_code FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            
            if row:
                return row['language_code']
            return None
        except Exception as e:
            logger.error(f"Error getting user language: {e}")
            return None
    
    def set_user_settings(self, user_id: int, settings: Dict) -> bool:
        """Update user settings"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Build update query dynamically
            updates = []
            values = []
            
            for key, value in settings.items():
                if key in ['temperature_unit', 'wind_unit', 'default_location', 'notification_enabled']:
                    updates.append(f"{key} = ?")
                    values.append(value)
            
            if updates:
                updates.append("updated_at = ?")
                values.append(datetime.now())
                values.append(user_id)
                
                query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
                cursor.execute(query, values)
                conn.commit()
            
            return True
        except Exception as e:
            logger.error(f"Error updating user settings: {e}")
            return False
    
    def add_favorite_location(self, user_id: int, location_name: str, 
                            latitude: float = None, longitude: float = None, 
                            is_default: bool = False) -> bool:
        """Add favorite location for user"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # If this is default, unset other defaults
            if is_default:
                cursor.execute('''
                    UPDATE user_locations SET is_default = 0 WHERE user_id = ?
                ''', (user_id,))
            
            cursor.execute('''
                INSERT INTO user_locations 
                (user_id, location_name, latitude, longitude, is_default)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, location_name, latitude, longitude, is_default))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding favorite location: {e}")
            return False
    
    def get_user_locations(self, user_id: int) -> List[Dict]:
        """Get user's favorite locations"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM user_locations 
                WHERE user_id = ? 
                ORDER BY is_default DESC, created_at DESC
            ''', (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting user locations: {e}")
            return []
    
    def log_weather_request(self, user_id: int, location: str, request_type: str,
                          response_time: float, success: bool, error_message: str = None) -> bool:
        """Log weather request for analytics"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO weather_requests 
                (user_id, location, request_type, response_time, success, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, location, request_type, response_time, success, error_message))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error logging weather request: {e}")
            return False
    
    def get_user_stats(self, user_id: int, days: int = 30) -> Dict:
        """Get user statistics"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            since_date = datetime.now() - timedelta(days=days)
            
            # Total requests
            cursor.execute('''
                SELECT COUNT(*) as total_requests,
                       COUNT(CASE WHEN success = 1 THEN 1 END) as successful_requests,
                       AVG(response_time) as avg_response_time
                FROM weather_requests 
                WHERE user_id = ? AND created_at >= ?
            ''', (user_id, since_date))
            
            stats = dict(cursor.fetchone())
            
            # Most queried locations
            cursor.execute('''
                SELECT location, COUNT(*) as query_count
                FROM weather_requests 
                WHERE user_id = ? AND created_at >= ?
                GROUP BY location
                ORDER BY query_count DESC
                LIMIT 5
            ''', (user_id, since_date))
            
            stats['top_locations'] = [dict(row) for row in cursor.fetchall()]
            
            return stats
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}
    
    def cache_weather_data(self, location_key: str, data_type: str, 
                          weather_data: Dict, ttl_minutes: int = 10) -> bool:
        """Cache weather data"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            expires_at = datetime.now() + timedelta(minutes=ttl_minutes)
            data_json = json.dumps(weather_data)
            
            cursor.execute('''
                INSERT OR REPLACE INTO weather_cache 
                (location_key, data_type, weather_data, expires_at)
                VALUES (?, ?, ?, ?)
            ''', (location_key, data_type, data_json, expires_at))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error caching weather data: {e}")
            return False
    
    def get_cached_weather_data(self, location_key: str, data_type: str) -> Optional[Dict]:
        """Get cached weather data"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT weather_data FROM weather_cache 
                WHERE location_key = ? AND data_type = ? AND expires_at > ?
            ''', (location_key, data_type, datetime.now()))
            
            row = cursor.fetchone()
            if row:
                return json.loads(row['weather_data'])
            return None
        except Exception as e:
            logger.error(f"Error getting cached weather data: {e}")
            return None
    
    def cleanup_old_data(self, days: int = 30) -> bool:
        """Clean up old data from database"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Clean old weather requests
            cursor.execute('DELETE FROM weather_requests WHERE created_at < ?', (cutoff_date,))
            
            # Clean expired cache
            cursor.execute('DELETE FROM weather_cache WHERE expires_at < ?', (datetime.now(),))
            
            # Clean old sessions
            cursor.execute('DELETE FROM user_sessions WHERE session_end < ?', (cutoff_date,))
            
            conn.commit()
            logger.info(f"Cleaned up old data older than {days} days")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return False
    
    def get_analytics_summary(self) -> Dict:
        """Get overall analytics summary"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Total users
            cursor.execute('SELECT COUNT(*) as total_users FROM users WHERE is_active = 1')
            total_users = cursor.fetchone()['total_users']
            
            # Requests today
            today = datetime.now().date()
            cursor.execute('''
                SELECT COUNT(*) as requests_today 
                FROM weather_requests 
                WHERE DATE(created_at) = ?
            ''', (today,))
            requests_today = cursor.fetchone()['requests_today']
            
            # Most popular locations
            cursor.execute('''
                SELECT location, COUNT(*) as query_count
                FROM weather_requests 
                WHERE created_at >= DATE('now', '-7 days')
                GROUP BY location
                ORDER BY query_count DESC
                LIMIT 10
            ''', )
            popular_locations = [dict(row) for row in cursor.fetchall()]
            
            # Language distribution
            cursor.execute('''
                SELECT language_code, COUNT(*) as user_count
                FROM users 
                WHERE is_active = 1
                GROUP BY language_code
                ORDER BY user_count DESC
            ''')
            language_stats = [dict(row) for row in cursor.fetchall()]
            
            return {
                'total_users': total_users,
                'requests_today': requests_today,
                'popular_locations': popular_locations,
                'language_stats': language_stats
            }
        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        if hasattr(self.local, 'connection'):
            self.local.connection.close()

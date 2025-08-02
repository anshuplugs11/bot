#!/usr/bin/env python3
"""
Utilities Module
Contains helper functions and utilities
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math

def format_temperature(temp: float, unit: str = 'celsius') -> str:
    """Format temperature with proper unit"""
    if unit.lower() == 'fahrenheit':
        temp_f = (temp * 9/5) + 32
        return f"{temp_f:.1f}°F"
    else:
        return f"{temp:.1f}°C"

def format_wind_speed(speed: float, unit: str = 'kmh') -> str:
    """Format wind speed with proper unit"""
    if unit.lower() == 'mph':
        speed_mph = speed * 0.621371
        return f"{speed_mph:.1f} mph"
    else:
        return f"{speed:.1f} km/h"

def get_weather_emoji(condition: str) -> str:
    """Get appropriate emoji for weather condition"""
    condition = condition.lower()
    
    emoji_map = {
        # Sunny/Clear
        'sunny': '☀️',
        'clear': '☀️',
        'fair': '🌤️',
        
        # Cloudy
        'cloudy': '☁️',
        'overcast': '☁️',
        'partly cloudy': '⛅',
        'mostly cloudy': '🌥️',
        
        # Rain
        'rain': '🌧️',
        'light rain': '🌦️',
        'heavy rain': '🌧️',
        'drizzle': '🌦️',
        'shower': '🌦️',
        
        # Snow
        'snow': '❄️',
        'light snow': '🌨️',
        'heavy snow': '❄️',
        'blizzard': '🌨️',
        'sleet': '🌨️',
        
        # Storms
        'thunder': '⛈️',
        'thunderstorm': '⛈️',
        'storm': '⛈️',
        'lightning': '⛈️',
        
        # Fog/Mist
        'fog': '🌫️',
        'mist': '🌫️',
        'haze': '🌫️',
        
        # Wind
        'windy': '💨',
        'breezy': '💨',
        
        # Extreme
        'tornado': '🌪️',
        'hurricane': '🌀',
        'typhoon': '🌀'
    }
    
    # Try exact match first
    for key, emoji in emoji_map.items():
        if key in condition:
            return emoji
    
    # Default emoji
    return '🌤️'

def get_wind_direction(degrees: int) -> str:
    """Convert wind direction degrees to compass direction"""
    directions = [
        'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
        'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'
    ]
    
    # Normalize degrees to 0-360
    degrees = degrees % 360
    
    # Each direction covers 22.5 degrees
    index = int((degrees + 11.25) / 22.5) % 16
    
    return directions[index]

def get_air_quality_description(aqi: int) -> Tuple[str, str]:
    """Get air quality description and color"""
    if aqi <= 50:
        return "Good", "🟢"
    elif aqi <= 100:
        return "Moderate", "🟡"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "🟠"
    elif aqi <= 200:
        return "Unhealthy", "🔴"
    elif aqi <= 300:
        return "Very Unhealthy", "🟣"
    else:
        return "Hazardous", "⚫"

def format_time_12hour(time_24: str) -> str:
    """Convert 24-hour time to 12-hour format"""
    try:
        time_obj = datetime.strptime(time_24, '%H:%M')
        return time_obj.strftime('%I:%M %p')
    except:
        return time_24

def format_date(date_str: str, format_type: str = 'short') -> str:
    """Format date string"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        
        if format_type == 'short':
            return date_obj.strftime('%a, %b %d')
        elif format_type == 'long':
            return date_obj.strftime('%A, %B %d, %Y')
        else:
            return date_obj.strftime('%m/%d/%Y')
    except:
        return date_str

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in kilometers"""
    # Haversine formula
    R = 6371  # Earth's radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat/2) * math.sin(dlat/2) + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2) * math.sin(dlon/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

def validate_coordinates(lat: float, lon: float) -> bool:
    """Validate latitude and longitude coordinates"""
    return -90 <= lat <= 90 and -180 <= lon <= 180

def parse_location_input(location_input: str) -> Dict[str, str]:
    """Parse location input and extract components"""
    # Clean input
    location_input = location_input.strip()
    
    # Check if it's coordinates (lat,lon format)
    coord_pattern = r'^(-?\d+\.?\d*),\s*(-?\d+\.?\d*)$'
    coord_match = re.match(coord_pattern, location_input)
    
    if coord_match:
        lat, lon = float(coord_match.group(1)), float(coord_match.group(2))
        if validate_coordinates(lat, lon):
            return {
                'type': 'coordinates',
                'latitude': lat,
                'longitude': lon,
                'query': location_input
            }
    
    # Parse city, country format
    if ',' in location_input:
        parts = [part.strip() for part in location_input.split(',')]
        return {
            'type': 'location',
            'city': parts[0],
            'country': parts[-1] if len(parts) > 1 else '',
            'region': parts[1] if len(parts) > 2 else '',
            'query': location_input
        }
    
    # Single location name
    return {
        'type': 'location',
        'city': location_input,
        'country': '',
        'region': '',
        'query': location_input
    }

def format_pressure(pressure: float, unit: str = 'mb') -> str:
    """Format atmospheric pressure with unit"""
    if unit.lower() == 'inhg':
        pressure_inhg = pressure * 0.02953
        return f"{pressure_inhg:.2f} inHg"
    else:
        return f"{pressure:.1f} mb"

def format_visibility(visibility: float, unit: str = 'km') -> str:
    """Format visibility with unit"""
    if unit.lower() == 'miles':
        visibility_miles = visibility * 0.621371
        return f"{visibility_miles:.1f} miles"
    else:
        return f"{visibility:.1f} km"

def get_uv_index_description(uv_index: float) -> Tuple[str, str]:
    """Get UV index description and color"""
    if uv_index <= 2:
        return "Low", "🟢"
    elif uv_index <= 5:
        return "Moderate", "🟡"
    elif uv_index <= 7:
        return "High", "🟠"
    elif uv_index <= 10:
        return "Very High", "🔴"
    else:
        return "Extreme", "🟣"

def format_humidity(humidity: int) -> str:
    """Format humidity percentage"""
    return f"{humidity}%"

def get_time_greeting(hour: int, language: str = 'en') -> str:
    """Get appropriate greeting based on time of day"""
    greetings = {
        'en': {
            'morning': 'Good morning',
            'afternoon': 'Good afternoon', 
            'evening': 'Good evening',
            'night': 'Good night'
        },
        'es': {
            'morning': 'Buenos días',
            'afternoon': 'Buenas tardes',
            'evening': 'Buenas tardes',
            'night': 'Buenas noches'
        },
        'fr': {
            'morning': 'Bonjour',
            'afternoon': 'Bon après-midi',
            'evening': 'Bonsoir',
            'night': 'Bonne nuit'
        },
        'de': {
            'morning': 'Guten Morgen',
            'afternoon': 'Guten Tag',
            'evening': 'Guten Abend',
            'night': 'Gute Nacht'
        }
    }
    
    if language not in greetings:
        language = 'en'
    
    if 5 <= hour < 12:
        return greetings[language]['morning']
    elif 12 <= hour < 17:
        return greetings[language]['afternoon']
    elif 17 <= hour < 21:
        return greetings[language]['evening']
    else:
        return greetings[language]['night']

def sanitize_location_name(location: str) -> str:
    """Sanitize location name for display"""
    # Remove extra whitespace
    location = ' '.join(location.split())
    
    # Capitalize each word
    location = location.title()
    
    return location

def is_valid_timezone(timezone: str) -> bool:
    """Check if timezone string is valid"""
    try:
        import pytz
        pytz.timezone(timezone)
        return True
    except:
        return False

def convert_timezone(dt: datetime, from_tz: str, to_tz: str) -> datetime:
    """Convert datetime from one timezone to another"""
    try:
        import pytz
        from_timezone = pytz.timezone(from_tz)
        to_timezone = pytz.timezone(to_tz)
        
        # Localize the datetime if it's naive
        if dt.tzinfo is None:
            dt = from_timezone.localize(dt)
        
        # Convert to target timezone
        return dt.astimezone(to_timezone)
    except:
        return dt

def truncate_text(text: str, max_length: int = 4000) -> str:
    """Truncate text to fit Telegram message limits"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def escape_markdown(text: str) -> str:
    """Escape markdown special characters"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

def get_moon_emoji(moon_phase: str) -> str:
    """Get appropriate emoji for moon phase"""
    phase = moon_phase.lower()
    
    moon_emojis = {
        'new moon': '🌑',
        'waxing crescent': '🌒',
        'first quarter': '🌓',
        'waxing gibbous': '🌔',
        'full moon': '🌕',
        'waning gibbous': '🌖',
        'third quarter': '🌗',
        'waning crescent': '🌘'
    }
    
    for phase_name, emoji in moon_emojis.items():
        if phase_name in phase:
            return emoji
    
    return '🌙'

def format_precipitation(amount: float, unit: str = 'mm') -> str:
    """Format precipitation amount"""
    if unit.lower() == 'inches':
        amount_inches = amount * 0.0393701
        return f"{amount_inches:.2f} in"
    else:
        return f"{amount:.1f} mm"

def get_severity_emoji(severity: str) -> str:
    """Get emoji for alert severity"""
    severity = severity.lower()
    
    severity_emojis = {
        'minor': '🟡',
        'moderate': '🟠', 
        'severe': '🔴',
        'extreme': '🟣'
    }
    
    return severity_emojis.get(severity, '⚠️')

def calculate_heat_index(temp_c: float, humidity: int) -> float:
    """Calculate heat index (feels like temperature)"""
    # Convert to Fahrenheit for calculation
    temp_f = (temp_c * 9/5) + 32
    
    if temp_f < 80 or humidity < 40:
        return temp_c
    
    # Heat index formula
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity 
          - 0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2
          - 5.481717e-2 * humidity**2 + 1.22874e-3 * temp_f**2 * humidity
          + 8.5282e-4 * temp_f * humidity**2 - 1.99e-6 * temp_f**2 * humidity**2)
    
    # Convert back to Celsius
    return (hi - 32) * 5/9

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"

def is_daytime(current_hour: int, sunrise_hour: int, sunset_hour: int) -> bool:
    """Check if current time is during daytime"""
    return sunrise_hour <= current_hour < sunset_hour

def get_comfort_level(temp: float, humidity: int) -> str:
    """Get comfort level description based on temperature and humidity"""
    if temp < 10:
        return "Very Cold"
    elif temp < 18:
        return "Cold"
    elif temp < 24:
        if humidity < 30:
            return "Comfortable (Dry)"
        elif humidity > 70:
            return "Comfortable (Humid)"
        else:
            return "Comfortable"
    elif temp < 30:
        if humidity > 60:
            return "Warm (Humid)"
        else:
            return "Warm"
    else:
        return "Hot"

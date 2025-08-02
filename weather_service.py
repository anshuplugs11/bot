#!/usr/bin/env python3
"""
Weather Service Module
Handles all weather API interactions
"""

import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.weatherapi.com/v1"
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API request"""
        try:
            session = await self._get_session()
            params['key'] = self.api_key
            
            url = f"{self.base_url}/{endpoint}"
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API request failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            return None
    
    async def get_current_weather(self, location: str) -> Optional[Dict]:
        """Get current weather data"""
        params = {
            'q': location,
            'aqi': 'yes'
        }
        
        data = await self._make_request('current.json', params)
        if not data:
            return None
        
        current = data.get('current', {})
        location_data = data.get('location', {})
        
        return {
            'location': f"{location_data.get('name', '')}, {location_data.get('country', '')}",
            'temperature': current.get('temp_c', 0),
            'feels_like': current.get('feelslike_c', 0),
            'humidity': current.get('humidity', 0),
            'wind_speed': current.get('wind_kph', 0),
            'wind_direction': current.get('wind_degree', 0),
            'condition': current.get('condition', {}).get('text', ''),
            'pressure': current.get('pressure_mb', 0),
            'visibility': current.get('vis_km', 0),
            'uv_index': current.get('uv', 0),
            'last_updated': current.get('last_updated', ''),
            'sunrise': '05:52 AM',  # These would come from astronomy API
            'sunset': '08:11 PM'
        }
    
    async def get_12hour_forecast(self, location: str) -> List[Dict]:
        """Get 12-hour forecast"""
        params = {
            'q': location,
            'hours': 24,
            'aqi': 'no'
        }
        
        data = await self._make_request('forecast.json', params)
        if not data:
            return []
        
        forecast = []
        forecast_data = data.get('forecast', {}).get('forecastday', [])
        
        if forecast_data:
            today = forecast_data[0]
            hours = today.get('hour', [])
            current_hour = datetime.now().hour
            
            # Get next 12 hours
            for i in range(12):
                hour_index = (current_hour + i) % 24
                if hour_index < len(hours):
                    hour_data = hours[hour_index]
                    
                    # Format time
                    time_obj = datetime.strptime(hour_data.get('time', ''), '%Y-%m-%d %H:%M')
                    time_str = time_obj.strftime('%I %p')
                    
                    forecast.append({
                        'time': f"{time_obj.strftime('%I %p')}",
                        'temperature': hour_data.get('temp_c', 0),
                        'condition': hour_data.get('condition', {}).get('text', ''),
                        'precipitation': hour_data.get('chance_of_rain', 0),
                        'wind_speed': hour_data.get('wind_kph', 0)
                    })
        
        return forecast
    
    async def get_7day_forecast(self, location: str) -> List[Dict]:
        """Get 7-day forecast"""
        params = {
            'q': location,
            'days': 7,
            'aqi': 'no'
        }
        
        data = await self._make_request('forecast.json', params)
        if not data:
            return []
        
        forecast = []
        forecast_data = data.get('forecast', {}).get('forecastday', [])
        
        for day_data in forecast_data:
            day = day_data.get('day', {})
            date_str = day_data.get('date', '')
            
            # Format date
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%a, %b %d')
            except:
                formatted_date = date_str
            
            forecast.append({
                'date': formatted_date,
                'temp_min': day.get('mintemp_c', 0),
                'temp_max': day.get('maxtemp_c', 0),
                'condition': day.get('condition', {}).get('text', ''),
                'precipitation_chance': day.get('daily_chance_of_rain', 0),
                'humidity': day.get('avghumidity', 0)
            })
        
        return forecast
    
    async def get_air_quality(self, location: str) -> Optional[Dict]:
        """Get air quality data"""
        params = {
            'q': location,
            'aqi': 'yes'
        }
        
        data = await self._make_request('current.json', params)
        if not data:
            return None
        
        current = data.get('current', {})
        air_quality = current.get('air_quality', {})
        
        # Calculate AQI status
        co = air_quality.get('co', 0)
        no2 = air_quality.get('no2', 0)
        o3 = air_quality.get('o3', 0)
        pm25 = air_quality.get('pm2_5', 0)
        pm10 = air_quality.get('pm10', 0)
        
        # Simple AQI calculation (this is simplified)
        aqi_value = max(pm25 * 2, pm10, no2 / 2, o3 / 2, co / 10)
        
        if aqi_value <= 50:
            status = "Good"
        elif aqi_value <= 100:
            status = "Moderate"
        elif aqi_value <= 150:
            status = "Unhealthy for Sensitive Groups"
        else:
            status = "Unhealthy"
        
        return {
            'aqi': int(aqi_value),
            'status': status,
            'co': round(co, 2),
            'no2': round(no2, 2),
            'o3': round(o3, 2),
            'pm25': round(pm25, 2),
            'pm10': round(pm10, 2)
        }
    
    async def get_weather_alerts(self, location: str) -> List[Dict]:
        """Get weather alerts"""
        params = {
            'q': location,
            'alerts': 'yes'
        }
        
        data = await self._make_request('current.json', params)
        if not data:
            return []
        
        alerts_data = data.get('alerts', {}).get('alert', [])
        alerts = []
        
        for alert in alerts_data:
            alerts.append({
                'title': alert.get('headline', ''),
                'description': alert.get('desc', ''),
                'severity': alert.get('severity', ''),
                'start': alert.get('effective', ''),
                'end': alert.get('expires', ''),
                'areas': alert.get('areas', '')
            })
        
        return alerts
    
    async def get_astronomy_data(self, location: str) -> Optional[Dict]:
        """Get astronomy data (sunrise, sunset, moon phase)"""
        params = {
            'q': location,
            'dt': datetime.now().strftime('%Y-%m-%d')
        }
        
        data = await self._make_request('astronomy.json', params)
        if not data:
            return None
        
        astronomy = data.get('astronomy', {}).get('astro', {})
        
        return {
            'sunrise': astronomy.get('sunrise', ''),
            'sunset': astronomy.get('sunset', ''),
            'moonrise': astronomy.get('moonrise', ''),
            'moonset': astronomy.get('moonset', ''),
            'moon_phase': astronomy.get('moon_phase', ''),
            'moon_illumination': astronomy.get('moon_illumination', 0)
        }
    
    async def search_locations(self, query: str) -> List[Dict]:
        """Search for locations"""
        params = {
            'q': query
        }
        
        data = await self._make_request('search.json', params)
        if not data:
            return []
        
        locations = []
        for location in data:
            locations.append({
                'name': location.get('name', ''),
                'region': location.get('region', ''),
                'country': location.get('country', ''),
                'lat': location.get('lat', 0),
                'lon': location.get('lon', 0)
            })
        
        return locations
    
    async def get_historical_weather(self, location: str, date: str) -> Optional[Dict]:
        """Get historical weather data"""
        params = {
            'q': location,
            'dt': date
        }
        
        data = await self._make_request('history.json', params)
        if not data:
            return None
        
        forecast_day = data.get('forecast', {}).get('forecastday', [])
        if not forecast_day:
            return None
        
        day = forecast_day[0].get('day', {})
        
        return {
            'date': date,
            'max_temp': day.get('maxtemp_c', 0),
            'min_temp': day.get('mintemp_c', 0),
            'avg_temp': day.get('avgtemp_c', 0),
            'condition': day.get('condition', {}).get('text', ''),
            'total_precipitation': day.get('totalprecip_mm', 0),
            'avg_humidity': day.get('avghumidity', 0),
            'max_wind': day.get('maxwind_kph', 0)
        }
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()

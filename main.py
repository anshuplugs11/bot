#!/usr/bin/env python3
"""
Advanced Weather Bot with Multi-language Support
Main application file
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from weather_service import WeatherService
from language_manager import LanguageManager
from config import Config
from utils import format_temperature, format_wind_speed, get_weather_emoji
from database import DatabaseManager

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class WeatherBot:
    def __init__(self):
        self.config = Config()
        self.weather_service = WeatherService(self.config.WEATHER_API_KEY)
        self.language_manager = LanguageManager()
        self.db = DatabaseManager()
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Get user's preferred language or default to English
        user_lang = self.db.get_user_language(chat_id) or 'en'
        
        welcome_text = self.language_manager.get_text('welcome', user_lang)
        
        # Create language selection keyboard
        keyboard = [
            [
                InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
                InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es")
            ],
            [
                InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"),
                InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text.format(name=user.first_name),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def language_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle language selection"""
        query = update.callback_query
        await query.answer()
        
        lang_code = query.data.split('_')[1]
        chat_id = query.message.chat_id
        
        # Save user's language preference
        self.db.set_user_language(chat_id, lang_code)
        
        confirmation_text = self.language_manager.get_text('language_set', lang_code)
        help_text = self.language_manager.get_text('help', lang_code)
        
        await query.edit_message_text(
            f"{confirmation_text}\n\n{help_text}",
            parse_mode=ParseMode.HTML
        )

    async def weather_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /weather command"""
        chat_id = update.effective_chat.id
        user_lang = self.db.get_user_language(chat_id) or 'en'
        
        if not context.args:
            prompt_text = self.language_manager.get_text('enter_location', user_lang)
            await update.message.reply_text(prompt_text)
            return
        
        location = ' '.join(context.args)
        await self.send_weather_info(update, location, user_lang)

    async def handle_location_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle location messages"""
        chat_id = update.effective_chat.id
        user_lang = self.db.get_user_language(chat_id) or 'en'
        
        if update.message.location:
            # Handle GPS location
            lat = update.message.location.latitude
            lon = update.message.location.longitude
            location = f"{lat},{lon}"
        else:
            # Handle text location
            location = update.message.text
        
        await self.send_weather_info(update, location, user_lang)

    async def send_weather_info(self, update: Update, location: str, user_lang: str):
        """Send comprehensive weather information"""
        try:
            loading_text = self.language_manager.get_text('loading', user_lang)
            message = await update.message.reply_text(loading_text)
            
            # Get weather data
            current_weather = await self.weather_service.get_current_weather(location)
            forecast_12h = await self.weather_service.get_12hour_forecast(location)
            forecast_7d = await self.weather_service.get_7day_forecast(location)
            air_quality = await self.weather_service.get_air_quality(location)
            
            # Create weather report
            weather_text = self.format_current_weather(current_weather, user_lang)
            
            # Create interactive keyboard
            keyboard = [
                [
                    InlineKeyboardButton(
                        self.language_manager.get_text('12h_forecast', user_lang),
                        callback_data=f"forecast_12h_{location}"
                    ),
                    InlineKeyboardButton(
                        self.language_manager.get_text('7d_forecast', user_lang),
                        callback_data=f"forecast_7d_{location}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        self.language_manager.get_text('air_quality', user_lang),
                        callback_data=f"air_quality_{location}"
                    ),
                    InlineKeyboardButton(
                        self.language_manager.get_text('weather_alerts', user_lang),
                        callback_data=f"alerts_{location}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        self.language_manager.get_text('refresh', user_lang),
                        callback_data=f"refresh_{location}"
                    ),
                    InlineKeyboardButton(
                        self.language_manager.get_text('maps_radar', user_lang),
                        callback_data=f"maps_{location}"
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await message.edit_text(
                weather_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            error_text = self.language_manager.get_text('error_occurred', user_lang)
            await update.message.reply_text(f"{error_text}: {str(e)}")

    def format_current_weather(self, weather_data: Dict, user_lang: str) -> str:
        """Format current weather data"""
        if not weather_data:
            return self.language_manager.get_text('no_data', user_lang)
        
        current_time = datetime.now().strftime("%I:%M %p")
        
        weather_emoji = get_weather_emoji(weather_data.get('condition', ''))
        temp = format_temperature(weather_data.get('temperature', 0))
        feels_like = format_temperature(weather_data.get('feels_like', 0))
        humidity = weather_data.get('humidity', 0)
        wind_speed = format_wind_speed(weather_data.get('wind_speed', 0))
        wind_dir = weather_data.get('wind_direction', 0)
        
        sunrise = weather_data.get('sunrise', '06:00 AM')
        sunset = weather_data.get('sunset', '08:00 PM')
        
        location_name = weather_data.get('location', 'Unknown')
        condition = weather_data.get('condition', 'Unknown')
        
        text = f"""
{weather_emoji} <b>{self.language_manager.get_text('current_weather', user_lang)}</b>
📍 {self.language_manager.get_text('location', user_lang)}: {location_name}
🕐 {self.language_manager.get_text('local_time', user_lang)}: {current_time}
🌡️ {self.language_manager.get_text('temperature', user_lang)}: {temp} ({self.language_manager.get_text('feels_like', user_lang)}: {feels_like})
💧 {self.language_manager.get_text('humidity', user_lang)}: {humidity}%
💨 {self.language_manager.get_text('wind', user_lang)}: {wind_speed} {self.language_manager.get_text('from', user_lang)} {wind_dir}°
🌅 {self.language_manager.get_text('sunrise', user_lang)}: {sunrise}
🌇 {self.language_manager.get_text('sunset', user_lang)}: {sunset}
☁️ {self.language_manager.get_text('weather', user_lang)}: {condition}
"""
        return text.strip()

    async def forecast_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle forecast callbacks"""
        query = update.callback_query
        await query.answer()
        
        chat_id = query.message.chat_id
        user_lang = self.db.get_user_language(chat_id) or 'en'
        
        callback_parts = query.data.split('_', 2)
        forecast_type = callback_parts[1]
        location = callback_parts[2] if len(callback_parts) > 2 else 'New York'
        
        try:
            if forecast_type == '12h':
                forecast_data = await self.weather_service.get_12hour_forecast(location)
                text = self.format_12hour_forecast(forecast_data, user_lang)
            elif forecast_type == '7d':
                forecast_data = await self.weather_service.get_7day_forecast(location)
                text = self.format_7day_forecast(forecast_data, user_lang)
            else:
                text = self.language_manager.get_text('invalid_request', user_lang)
            
            # Add back button
            keyboard = [[InlineKeyboardButton(
                self.language_manager.get_text('back_to_main', user_lang),
                callback_data=f"refresh_{location}"
            )]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            error_text = self.language_manager.get_text('error_occurred', user_lang)
            await query.edit_message_text(f"{error_text}: {str(e)}")

    def format_12hour_forecast(self, forecast_data: List[Dict], user_lang: str) -> str:
        """Format 12-hour forecast"""
        if not forecast_data:
            return self.language_manager.get_text('no_data', user_lang)
        
        text = f"📊 <b>{self.language_manager.get_text('12h_forecast_title', user_lang)}</b>\n\n"
        
        for hour_data in forecast_data[:12]:
            time = hour_data.get('time', '')
            temp = format_temperature(hour_data.get('temperature', 0))
            condition = hour_data.get('condition', '')
            emoji = get_weather_emoji(condition)
            
            text += f"{time}: {temp} {emoji} {condition}\n"
        
        return text

    def format_7day_forecast(self, forecast_data: List[Dict], user_lang: str) -> str:
        """Format 7-day forecast"""
        if not forecast_data:
            return self.language_manager.get_text('no_data', user_lang)
        
        text = f"📅 <b>{self.language_manager.get_text('7d_forecast_title', user_lang)}</b>\n\n"
        
        for day_data in forecast_data[:7]:
            date = day_data.get('date', '')
            temp_min = format_temperature(day_data.get('temp_min', 0))
            temp_max = format_temperature(day_data.get('temp_max', 0))
            condition = day_data.get('condition', '')
            emoji = get_weather_emoji(condition)
            
            text += f"{date}: {temp_min}/{temp_max} {emoji} {condition}\n"
        
        return text

    async def air_quality_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle air quality callback"""
        query = update.callback_query
        await query.answer()
        
        chat_id = query.message.chat_id
        user_lang = self.db.get_user_language(chat_id) or 'en'
        
        location = query.data.split('_', 2)[2] if len(query.data.split('_', 2)) > 2 else 'New York'
        
        try:
            air_data = await self.weather_service.get_air_quality(location)
            text = self.format_air_quality(air_data, user_lang)
            
            keyboard = [[InlineKeyboardButton(
                self.language_manager.get_text('back_to_main', user_lang),
                callback_data=f"refresh_{location}"
            )]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            error_text = self.language_manager.get_text('error_occurred', user_lang)
            await query.edit_message_text(f"{error_text}: {str(e)}")

    def format_air_quality(self, air_data: Dict, user_lang: str) -> str:
        """Format air quality data"""
        if not air_data:
            return self.language_manager.get_text('no_data', user_lang)
        
        aqi = air_data.get('aqi', 0)
        status = air_data.get('status', 'Unknown')
        
        # Get AQI emoji based on value
        if aqi <= 50:
            aqi_emoji = "🟢"
        elif aqi <= 100:
            aqi_emoji = "🟡"
        elif aqi <= 150:
            aqi_emoji = "🟠"
        else:
            aqi_emoji = "🔴"
        
        text = f"""
🌬️ <b>{self.language_manager.get_text('air_quality_title', user_lang)}</b>

{self.language_manager.get_text('overall_aqi', user_lang)}: {status} {aqi_emoji}
CO: {air_data.get('co', 0)} μg/m³
NO₂: {air_data.get('no2', 0)} μg/m³
O₃: {air_data.get('o3', 0)} μg/m³
PM2.5: {air_data.get('pm25', 0)} μg/m³
PM10: {air_data.get('pm10', 0)} μg/m³
"""
        return text.strip()

    async def alerts_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle weather alerts callback"""
        query = update.callback_query
        await query.answer()
        
        chat_id = query.message.chat_id
        user_lang = self.db.get_user_language(chat_id) or 'en'
        
        location = query.data.split('_', 1)[1] if len(query.data.split('_', 1)) > 1 else 'New York'
        
        try:
            alerts = await self.weather_service.get_weather_alerts(location)
            
            if alerts:
                text = f"⚠️ <b>{self.language_manager.get_text('weather_alerts_title', user_lang)}</b>\n\n"
                for alert in alerts:
                    text += f"🚨 {alert.get('title', '')}\n"
                    text += f"📅 {alert.get('start', '')} - {alert.get('end', '')}\n"
                    text += f"📝 {alert.get('description', '')}\n\n"
            else:
                text = f"✅ {self.language_manager.get_text('no_active_alerts', user_lang)}"
            
            keyboard = [[InlineKeyboardButton(
                self.language_manager.get_text('back_to_main', user_lang),
                callback_data=f"refresh_{location}"
            )]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            error_text = self.language_manager.get_text('error_occurred', user_lang)
            await query.edit_message_text(f"{error_text}: {str(e)}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        chat_id = update.effective_chat.id
        user_lang = self.db.get_user_language(chat_id) or 'en'
        
        help_text = self.language_manager.get_text('help_detailed', user_lang)
        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

    def run(self):
        """Run the bot"""
        # Create application
        application = Application.builder().token(self.config.BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("weather", self.weather_command))
        application.add_handler(CommandHandler("help", self.help_command))
        
        # Callback handlers
        application.add_handler(CallbackQueryHandler(self.language_callback, pattern="^lang_"))
        application.add_handler(CallbackQueryHandler(self.forecast_callback, pattern="^forecast_"))
        application.add_handler(CallbackQueryHandler(self.air_quality_callback, pattern="^air_quality_"))
        application.add_handler(CallbackQueryHandler(self.alerts_callback, pattern="^alerts_"))
        application.add_handler(CallbackQueryHandler(self.send_weather_callback, pattern="^refresh_"))
        
        # Message handlers
        application.add_handler(MessageHandler(filters.LOCATION, self.handle_location_message))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_location_message))
        
        # Start the bot
        logger.info("Starting Weather Bot...")
        application.run_polling()

    async def send_weather_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle refresh weather callback"""
        query = update.callback_query
        await query.answer()
        
        chat_id = query.message.chat_id
        user_lang = self.db.get_user_language(chat_id) or 'en'
        
        location = query.data.split('_', 1)[1] if len(query.data.split('_', 1)) > 1 else 'New York'
        
        # Create a fake update object for sending weather info
        class FakeMessage:
            def __init__(self, message):
                self.message = message
                self.effective_chat = message.chat
            
            async def reply_text(self, text, **kwargs):
                return await self.message.edit_text(text, **kwargs)
        
        fake_update = FakeMessage(query.message)
        await self.send_weather_info(fake_update, location, user_lang)

if __name__ == "__main__":
    bot = WeatherBot()
    bot.run()

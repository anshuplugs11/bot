#!/usr/bin/env python3
"""
Language Manager Module
Handles multi-language support for the weather bot
"""

import json
from typing import Dict

class LanguageManager:
    def __init__(self):
        self.translations = {
            'en': {
                'welcome': 'Welcome <b>{name}</b>! 🌤️\n\nI\'m your advanced weather bot. Select your preferred language:',
                'language_set': '✅ Language set to English!',
                'help': '📖 <b>How to use:</b>\n\n• Send me a location name\n• Share your GPS location\n• Use /weather [location]\n• Use /help for more info',
                'help_detailed': '''📖 <b>Weather Bot Help</b>

🌍 <b>Getting Weather:</b>
• Send any location name (e.g., "New York", "London")
• Share your GPS location
• Use command: /weather [location]

🔧 <b>Available Commands:</b>
• /start - Start the bot and select language
• /weather [location] - Get weather for specific location
• /help - Show this help message

📊 <b>Features:</b>
• Current weather conditions
• 12-hour detailed forecast
• 7-day weather forecast
• Air quality information
• Weather alerts and warnings
• Interactive buttons for easy navigation

🌐 <b>Supported Languages:</b>
• 🇺🇸 English
• 🇪🇸 Spanish
• 🇫🇷 French
• 🇩🇪 German

📱 <b>Tips:</b>
• Use location names like "City, Country" for better accuracy
• GPS location gives most accurate results
• All temperatures are shown in Celsius

Enjoy using the weather bot! 🌤️''',
                'enter_location': '📍 Please enter a location name or share your GPS location.',
                'loading': '⏳ Loading weather data...',
                'current_weather': 'Current Weather',
                'location': 'Location',
                'local_time': 'Local Time',
                'temperature': 'Temperature',
                'feels_like': 'Feels like',
                'humidity': 'Humidity',
                'wind': 'Wind',
                'from': 'from',
                'sunrise': 'Sunrise',
                'sunset': 'Sunset',
                'weather': 'Weather',
                '12h_forecast': '12h Forecast',
                '7d_forecast': '7-Day Forecast',
                'air_quality': 'Air Quality',
                'weather_alerts': 'Weather Alerts',
                'refresh': 'Refresh Current',
                'maps_radar': 'Maps & Radar',
                'back_to_main': '🔙 Back to Main',
                '12h_forecast_title': '12-Hour Forecast',
                '7d_forecast_title': '7-Day Forecast',
                'air_quality_title': 'Air Quality',
                'overall_aqi': 'Overall AQI',
                'weather_alerts_title': 'Weather Alerts',
                'no_active_alerts': 'No active weather alerts',
                'error_occurred': 'An error occurred',
                'no_data': 'No weather data available',
                'invalid_request': 'Invalid request'
            },
            'es': {
                'welcome': '¡Bienvenido <b>{name}</b>! 🌤️\n\nSoy tu bot meteorológico avanzado. Selecciona tu idioma preferido:',
                'language_set': '✅ ¡Idioma configurado en Español!',
                'help': '📖 <b>Cómo usar:</b>\n\n• Envíame el nombre de una ubicación\n• Comparte tu ubicación GPS\n• Usa /weather [ubicación]\n• Usa /help para más información',
                'help_detailed': '''📖 <b>Ayuda del Bot Meteorológico</b>

🌍 <b>Obtener el Clima:</b>
• Envía cualquier nombre de ubicación (ej., "Madrid", "Barcelona")
• Comparte tu ubicación GPS
• Usa el comando: /weather [ubicación]

🔧 <b>Comandos Disponibles:</b>
• /start - Iniciar el bot y seleccionar idioma
• /weather [ubicación] - Obtener clima para ubicación específica
• /help - Mostrar este mensaje de ayuda

📊 <b>Características:</b>
• Condiciones climáticas actuales
• Pronóstico detallado de 12 horas
• Pronóstico meteorológico de 7 días
• Información de calidad del aire
• Alertas y avisos meteorológicos
• Botones interactivos para navegación fácil

🌐 <b>Idiomas Soportados:</b>
• 🇺🇸 Inglés
• 🇪🇸 Español
• 🇫🇷 Francés
• 🇩🇪 Alemán

📱 <b>Consejos:</b>
• Usa nombres de ubicación como "Ciudad, País" para mejor precisión
• La ubicación GPS da resultados más precisos
• Todas las temperaturas se muestran en Celsius

¡Disfruta usando el bot meteorológico! 🌤️''',
                'enter_location': '📍 Por favor, ingresa el nombre de una ubicación o comparte tu ubicación GPS.',
                'loading': '⏳ Cargando datos meteorológicos...',
                'current_weather': 'Clima Actual',
                'location': 'Ubicación',
                'local_time': 'Hora Local',
                'temperature': 'Temperatura',
                'feels_like': 'Sensación térmica',
                'humidity': 'Humedad',
                'wind': 'Viento',
                'from': 'desde',
                'sunrise': 'Amanecer',
                'sunset': 'Atardecer',
                'weather': 'Clima',
                '12h_forecast': 'Pronóstico 12h',
                '7d_forecast': 'Pronóstico 7 Días',
                'air_quality': 'Calidad del Aire',
                'weather_alerts': 'Alertas Meteorológicas',
                'refresh': 'Actualizar Actual',
                'maps_radar': 'Mapas y Radar',
                'back_to_main': '🔙 Volver al Principal',
                '12h_forecast_title': 'Pronóstico de 12 Horas',
                '7d_forecast_title': 'Pronóstico de 7 Días',
                'air_quality_title': 'Calidad del Aire',
                'overall_aqi': 'ICA General',
                'weather_alerts_title': 'Alertas Meteorológicas',
                'no_active_alerts': 'No hay alertas meteorológicas activas',
                'error_occurred': 'Ocurrió un error',
                'no_data': 'No hay datos meteorológicos disponibles',
                'invalid_request': 'Solicitud inválida'
            },
            'fr': {
                'welcome': 'Bienvenue <b>{name}</b>! 🌤️\n\nJe suis votre bot météo avancé. Sélectionnez votre langue préférée:',
                'language_set': '✅ Langue définie en Français!',
                'help': '📖 <b>Comment utiliser:</b>\n\n• Envoyez-moi un nom de lieu\n• Partagez votre localisation GPS\n• Utilisez /weather [lieu]\n• Utilisez /help pour plus d\'infos',
                'help_detailed': '''📖 <b>Aide du Bot Météo</b>

🌍 <b>Obtenir la Météo:</b>
• Envoyez n'importe quel nom de lieu (ex., "Paris", "Lyon")
• Partagez votre localisation GPS
• Utilisez la commande: /weather [lieu]

🔧 <b>Commandes Disponibles:</b>
• /start - Démarrer le bot et sélectionner la langue
• /weather [lieu] - Obtenir la météo pour un lieu spécifique
• /help - Afficher ce message d'aide

📊 <b>Fonctionnalités:</b>
• Conditions météorologiques actuelles
• Prévisions détaillées sur 12 heures
• Prévisions météorologiques sur 7 jours
• Informations sur la qualité de l'air
• Alertes et avertissements météo
• Boutons interactifs pour une navigation facile

🌐 <b>Langues Supportées:</b>
• 🇺🇸 Anglais
• 🇪🇸 Espagnol
• 🇫🇷 Français
• 🇩🇪 Allemand

📱 <b>Conseils:</b>
• Utilisez des noms de lieux comme "Ville, Pays" pour une meilleure précision
• La localisation GPS donne les résultats les plus précis
• Toutes les températures sont affichées en Celsius

Profitez du bot météo! 🌤️''',
                'enter_location': '📍 Veuillez entrer un nom de lieu ou partager votre localisation GPS.',
                'loading': '⏳ Chargement des données météo...',
                'current_weather': 'Météo Actuelle',
                'location': 'Localisation',
                'local_time': 'Heure Locale',
                'temperature': 'Température',
                'feels_like': 'Ressenti',
                'humidity': 'Humidité',
                'wind': 'Vent',
                'from': 'de',
                'sunrise': 'Lever du soleil',
                'sunset': 'Coucher du soleil',
                'weather': 'Météo',
                '12h_forecast': 'Prévisions 12h',
                '7d_forecast': 'Prévisions 7 Jours',
                'air_quality': 'Qualité de l\'Air',
                'weather_alerts': 'Alertes Météo',
                'refresh': 'Actualiser Actuel',
                'maps_radar': 'Cartes et Radar',
                'back_to_main': '🔙 Retour au Principal',
                '12h_forecast_title': 'Prévisions sur 12 Heures',
                '7d_forecast_title': 'Prévisions sur 7 Jours',
                'air_quality_title': 'Qualité de l\'Air',
                'overall_aqi': 'IQA Global',
                'weather_alerts_title': 'Alertes Météorologiques',
                'no_active_alerts': 'Aucune alerte météorologique active',
                'error_occurred': 'Une erreur s\'est produite',
                'no_data': 'Aucune donnée météo disponible',
                'invalid_request': 'Demande invalide'
            },
            'de': {
                'welcome': 'Willkommen <b>{name}</b>! 🌤️\n\nIch bin Ihr fortschrittlicher Wetter-Bot. Wählen Sie Ihre bevorzugte Sprache:',
                'language_set': '✅ Sprache auf Deutsch eingestellt!',
                'help': '📖 <b>Verwendung:</b>\n\n• Senden Sie mir einen Ortsnamen\n• Teilen Sie Ihren GPS-Standort\n• Verwenden Sie /weather [Ort]\n• Verwenden Sie /help für weitere Infos',
                'help_detailed': '''📖 <b>Wetter-Bot Hilfe</b>

🌍 <b>Wetter Abrufen:</b>
• Senden Sie einen beliebigen Ortsnamen (z.B. "Berlin", "München")
• Teilen Sie Ihren GPS-Standort
• Verwenden Sie den Befehl: /weather [Ort]

🔧 <b>Verfügbare Befehle:</b>
• /start - Bot starten und Sprache wählen
• /weather [Ort] - Wetter für bestimmten Ort abrufen
• /help - Diese Hilfenachricht anzeigen

📊 <b>Funktionen:</b>
• Aktuelle Wetterbedingungen
• Detaillierte 12-Stunden-Vorhersage
• 7-Tage-Wettervorhersage
• Luftqualitätsinformationen
• Wetterwarnungen und -hinweise
• Interaktive Schaltflächen für einfache Navigation

🌐 <b>Unterstützte Sprachen:</b>
• 🇺🇸 Englisch
• 🇪🇸 Spanisch
• 🇫🇷 Französisch
• 🇩🇪 Deutsch

📱 <b>Tipps:</b>
• Verwenden Sie Ortsnamen wie "Stadt, Land" für bessere Genauigkeit
• GPS-Standort liefert die genauesten Ergebnisse
• Alle Temperaturen werden in Celsius angezeigt

Viel Spaß mit dem Wetter-Bot! 🌤️''',
                'enter_location': '📍 Bitte geben Sie einen Ortsnamen ein oder teilen Sie Ihren GPS-Standort.',
                'loading': '⏳ Lade Wetterdaten...',
                'current_weather': 'Aktuelles Wetter',
                'location': 'Standort',
                'local_time': 'Ortszeit',
                'temperature': 'Temperatur',
                'feels_like': 'Gefühlt wie',
                'humidity': 'Luftfeuchtigkeit',
                'wind': 'Wind',
                'from': 'aus',
                'sunrise': 'Sonnenaufgang',
                'sunset': 'Sonnenuntergang',
                'weather': 'Wetter',
                '12h_forecast': '12h Vorhersage',
                '7d_forecast': '7-Tage Vorhersage',
                'air_quality': 'Luftqualität',
                'weather_alerts': 'Wetterwarnungen',
                'refresh': 'Aktuell Aktualisieren',
                'maps_radar': 'Karten & Radar',
                'back_to_main': '🔙 Zurück zum Hauptmenü',
                '12h_forecast_title': '12-Stunden-Vorhersage',
                '7d_forecast_title': '7-Tage-Vorhersage',
                'air_quality_title': 'Luftqualität',
                'overall_aqi': 'Gesamt-AQI',
                'weather_alerts_title': 'Wetterwarnungen',
                'no_active_alerts': 'Keine aktiven Wetterwarnungen',
                'error_occurred': 'Ein Fehler ist aufgetreten',
                'no_data': 'Keine Wetterdaten verfügbar',
                'invalid_request': 'Ungültige Anfrage'
            }
        }
    
    def get_text(self, key: str, language: str = 'en') -> str:
        """Get translated text for a given key and language"""
        if language not in self.translations:
            language = 'en'  # Fallback to English
        
        return self.translations[language].get(key, self.translations['en'].get(key, key))
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return {
            'en': '🇺🇸 English',
            'es': '🇪🇸 Español', 
            'fr': '🇫🇷 Français',
            'de': '🇩🇪 Deutsch'
        }
    
    def is_supported_language(self, language_code: str) -> bool:
        """Check if language is supported"""
        return language_code in self.translations

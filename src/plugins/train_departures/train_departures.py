from plugins.base_plugin.base_plugin import BasePlugin
import logging
import requests
import base64
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

class TrainDepartures(BasePlugin):
    def generate_settings_template(self):
        template_params = super().generate_settings_template()
        template_params['api_key'] = {
            "required": True,
            "service": "Realtime Trains",
            "expected_key_username": "RTT_API_USERNAME",
            "expected_key_password": "RTT_API_PASSWORD"
        }
        template_params['style_settings'] = True
        return template_params

    def generate_image(self, settings, device_config):
        # Get API credentials from environment variables
        username = device_config.load_env_key("RTT_API_USERNAME")
        password = device_config.load_env_key("RTT_API_PASSWORD")
        
        if not username or not password:
            raise RuntimeError("Realtime Trains API credentials not configured. Please set RTT_API_USERNAME and RTT_API_PASSWORD in your .env file.")
        
        # Get station code from settings
        station_code = settings.get('station_code')
        if not station_code:
            raise RuntimeError("Station code is required.")
        
        # Get optional filter station
        filter_station = settings.get('filter_station', '')
        
        # Fetch train departures data
        departures_data = self.get_departures(username, password, station_code, filter_station)
        
        # Get dimensions based on device orientation
        dimensions = device_config.get_resolution()
        if device_config.get_config("orientation") == "vertical":
            dimensions = dimensions[::-1]
        
        # Get timezone for time formatting
        timezone = device_config.get_config("timezone", default="Europe/London")
        tz = pytz.timezone(timezone)
        
        # Parse the departures data
        template_params = self.parse_departures_data(departures_data, tz)
        template_params["plugin_settings"] = settings
        
        # Render the image
        image = self.render_image(dimensions, "train_departures.html", "train_departures.css", template_params)
        
        if not image:
            raise RuntimeError("Failed to generate image, please check logs.")
        
        return image
    
    def get_departures(self, username, password, station_code, filter_station=''):
        auth = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth}"
        }
        
        # Build the URL based on whether a filter station is provided
        if filter_station:
            url = f"https://api.rtt.io/api/v1/json/search/{station_code}/to/{filter_station}"
        else:
            url = f"https://api.rtt.io/api/v1/json/search/{station_code}"
        
        try:
            # Make the API request
            response = requests.get(url, headers=headers)
            
            if not 200 <= response.status_code < 300:
                logger.error(f"Failed to retrieve train departures: {response.content}")
                raise RuntimeError("Failed to retrieve train departures. Please check your station code and API credentials.")
            
            return response.json()
        except Exception as e:
            logger.error(f"Error retrieving train departures: {str(e)}")
            return None
    
    def parse_departures_data(self, data, tz):
        if data is None:
            logger.error("No train departures data received from API")
            return {
                'station_name': 'Data Unavailable',
                'filter_info': None,
                'departures': [],
                'current_time': datetime.now(tz).strftime('%H:%M'),
                'current_date': datetime.now(tz).strftime('%A, %d %B %Y'),
                'error_message': 'Unable to retrieve train information'
            }
    
        location_name = data.get('location', {}).get('name', 'Unknown Station')
        
        # Get filter information if available
        filter_info = None
        if data.get('filter'):
            filter_from = data.get('filter', {}).get('from', {}).get('name')
            filter_to = data.get('filter', {}).get('to', {}).get('name')
            if filter_from and filter_to:
                filter_info = f"{filter_from} → {filter_to}"
        
        # Parse services (limit to 5)
        departures = []
        for service in data.get('services', [])[:5]:
            loc_detail = service.get('locationDetail', {})
            
            # Get departure time
            departure_time = loc_detail.get('gbttBookedDeparture', '')
            if loc_detail.get('realtimeDeparture'):
                departure_time = loc_detail.get('realtimeDeparture')
                
            # Get platform
            platform = loc_detail.get('platform', '')
            platform_confirmed = loc_detail.get('platformConfirmed', False)
            
            # Check if service is cancelled
            is_cancelled = "CANCELLED" in loc_detail.get('displayAs', '')
            cancel_reason = loc_detail.get('cancelReasonShortText', '')
            
            # Get destination
            destination = "Unknown"
            if loc_detail.get('destination'):
                destination = loc_detail.get('destination')[0].get('description', 'Unknown')
            
            # Get operator
            operator = service.get('atocName', 'Unknown')
            
            # Get service type
            service_type = service.get('serviceType', 'train')

            # Get lateness (if available)
            lateness = 0
            if loc_detail.get('realtimeGbttDepartureLateness') is not None:
                lateness = loc_detail.get('realtimeGbttDepartureLateness')
            
            # Format departure time for display
            time_formatted = departure_time
            if len(departure_time) == 4:
                hour = int(departure_time[:2])
                minute = departure_time[2:]
                time_formatted = f"{hour}:{minute}"
            
            # Train identity
            train_id = service.get('trainIdentity', '')
            
            departures.append({
                'time': time_formatted,
                'destination': destination,
                'platform': platform,
                'platform_confirmed': platform_confirmed,
                'is_cancelled': is_cancelled,
                'cancel_reason': cancel_reason,
                'operator': operator,
                'service_type': service_type,
                'lateness': lateness,
                'train_id': train_id
            })
        
        return {
            'station_name': location_name,
            'filter_info': filter_info,
            'departures': departures,
            'current_time': datetime.now(tz).strftime('%H:%M'),
            'current_date': datetime.now(tz).strftime('%A, %d %B %Y')
        } 
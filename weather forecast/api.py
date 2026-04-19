import requests
import config

class WeatherAPI:
    def __init__(self, api_key=None):
        self.api_key = (api_key or config.API_KEY).strip()
        self.base_url = config.BASE_URL

    def get_current_weather(self, city):
        """Fetch current weather for a city"""
        url = f"{self.base_url}weather?q={city}&appid={self.api_key}&units={config.UNIT}&lang={config.LANGUAGE}"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if response.status_code == 401:
                raise Exception("Invalid API Key. If you just created it, please wait 30-60 minutes for activation.")
            if response.status_code != 200:
                raise Exception(data.get("message", "City not found"))
            return data
        except requests.exceptions.ConnectionError:
            raise Exception("No Internet Connection")
        except Exception as e:
            raise e

    def get_forecast(self, city):
        """Fetch 5-day forecast (3-hour steps)"""
        url = f"{self.base_url}forecast?q={city}&appid={self.api_key}&units={config.UNIT}&lang={config.LANGUAGE}"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if response.status_code == 401:
                raise Exception("Activation Pending. Please wait 30-60 mins.")
            if response.status_code != 200:
                raise Exception(data.get("message", "Forecast unavailable"))
            return data
        except requests.exceptions.ConnectionError:
            raise Exception("No Internet Connection")
        except Exception as e:
            raise e

    def get_auto_location(self):
        """Get current city using IP geolocation"""
        try:
            response = requests.get("http://ip-api.com/json", timeout=5)
            data = response.json()
            if data.get("status") == "success":
                return data.get("city")
            return None
        except:
            return None

    def get_icon_url(self, icon_code):
        """Generate URL for weather icon"""
        return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

    def get_location_suggestions(self, query):
        """Fetch city suggestions using Geocoding API"""
        if not query or len(query) < 2:
            return []
        
        # OpenWeather Geocoding API
        url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={self.api_key}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Extract formatted name for dropdown (e.g., "City, State, Country")
                suggestions = []
                for item in data:
                    name = item.get("name", "")
                    state = item.get("state", "")
                    country = item.get("country", "")
                    
                    full_name = name
                    if state:
                        full_name += f", {state}"
                    if country:
                        full_name += f", {country}"
                    
                    suggestions.append({
                        "display": full_name,
                        "city": name
                    })
                return suggestions
            return []
        except:
            return []

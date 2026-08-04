import requests
from typing import Dict, Any
from components.state import WeatherAgentState
from components.config import config
from components.helper_functions import (
    classify_temperature, 
    get_weather_description, 
    get_greeting,
    format_local_time
)

def fetch_location_data(state: WeatherAgentState) -> WeatherAgentState:
    """
    Fetch location data based on IP address using ipapi.co service.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with location_data populated
    """
    try:
        response = requests.get(
            config.LOCATION_API_URL,
            timeout=config.REQUEST_TIMEOUT
        )
        response.raise_for_status()
        
        location_data = response.json()
        
        # Validate required fields
        required_fields = ['city', 'region', 'country_name', 'latitude', 'longitude', 'utc_offset', 'timezone']
        for field in required_fields:
            if field not in location_data:
                raise ValueError(f"Missing required field: {field}")
        
        state["location_data"] = location_data
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch location data: {str(e)}")
    except ValueError as e:
        raise Exception(f"Invalid location data received: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error fetching location: {str(e)}")
    
    return state

def fetch_weather_data(state: WeatherAgentState) -> WeatherAgentState:
    """
    Fetch current weather data using Open-Meteo API based on location coordinates.
    
    Args:
        state: Current agent state with location_data populated
        
    Returns:
        Updated state with weather_data populated
    """
    if not state.get("location_data"):
        raise Exception("Location data not available for weather fetch")
    
    location = state["location_data"]
    
    try:
        # Construct weather API URL with parameters
        params = {
            'latitude': location['latitude'],
            'longitude': location['longitude'],
            'current_weather': 'true'
        }
        
        response = requests.get(
            config.WEATHER_API_BASE_URL,
            params=params,
            timeout=config.REQUEST_TIMEOUT
        )
        response.raise_for_status()
        
        weather_data = response.json()
        
        # Validate required fields
        if 'current_weather' not in weather_data:
            raise ValueError("Missing current_weather data in response")
        
        required_weather_fields = ['time', 'temperature', 'windspeed', 'winddirection', 'is_day', 'weathercode']
        current_weather = weather_data['current_weather']
        
        for field in required_weather_fields:
            if field not in current_weather:
                raise ValueError(f"Missing required weather field: {field}")
        
        state["weather_data"] = weather_data
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch weather data: {str(e)}")
    except ValueError as e:
        raise Exception(f"Invalid weather data received: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error fetching weather: {str(e)}")
    
    return state

def generate_weather_info(state: WeatherAgentState) -> WeatherAgentState:
    """
    Generate formatted weather information string combining location and weather data.
    
    Args:
        state: Current agent state with location_data and weather_data populated
        
    Returns:
        Updated state with weather_info populated
    """
    if not state.get("location_data") or not state.get("weather_data"):
        raise Exception("Location or weather data not available for info generation")
    
    location = state["location_data"]
    weather = state["weather_data"]["current_weather"]
    units = state["weather_data"].get("current_weather_units", {})
    
    try:
        # Extract data
        name = state["name"]
        city = location["city"]
        region = location["region"]
        country = location["country_name"]
        utc_offset = location["utc_offset"]
        
        temperature = weather["temperature"]
        temp_unit = units.get("temperature", "°C")
        windspeed = weather["windspeed"]
        # wind_unit = units.get("windspeed", "km/h")
        is_day = weather["is_day"]
        weather_code = weather["weathercode"]
        utc_time = weather["time"]
        
        # Generate components
        greeting = get_greeting(is_day)
        temp_classification = classify_temperature(temperature)
        weather_description = get_weather_description(weather_code)
        time_info = format_local_time(utc_time, utc_offset)
        wind_unit = units.get("windspeed", "km/h")
        # Build comprehensive weather info string
        weather_info_parts = [
            f"Time: {time_info}",
            "",
            f"{greeting}, {name}!",
            "",
            f"Your current location: {city}, {region}, {country}",
            "",
            f"Current weather conditions:",
            f"• {weather_description}",
            f"• Temperature: {temperature}{temp_unit} ({temp_classification})",
            f"• Wind: {windspeed} {wind_unit}"
        ]
        
        state["weather_info"] = "\n".join(weather_info_parts)
        
    except KeyError as e:
        raise Exception(f"Missing data field for weather info generation: {str(e)}")
    except Exception as e:
        raise Exception(f"Error generating weather info: {str(e)}")
    
    return state
import math
from typing import List, Tuple

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r

def is_point_in_service_area(point_lat: float, point_lon: float, 
                           center_lat: float, center_lon: float, radius_km: float) -> bool:
    """
    Check if a point is within a service provider's service area
    """
    distance = calculate_distance(point_lat, point_lon, center_lat, center_lon)
    return distance <= radius_km

def find_nearby_providers(customer_lat: float, customer_lon: float, 
                         providers: List[dict], max_distance_km: float = 50) -> List[dict]:
    """
    Find service providers within a specified distance from customer location
    """
    nearby_providers = []
    
    for provider in providers:
        if 'latitude' in provider and 'longitude' in provider:
            distance = calculate_distance(
                customer_lat, customer_lon,
                provider['latitude'], provider['longitude']
            )
            
            if distance <= max_distance_km:
                provider['distance_km'] = round(distance, 2)
                nearby_providers.append(provider)
    
    # Sort by distance
    nearby_providers.sort(key=lambda x: x['distance_km'])
    
    return nearby_providers

def estimate_travel_time(distance_km: float, avg_speed_kmh: float = 30) -> int:
    """
    Estimate travel time in minutes based on distance and average speed
    Default speed is 30 km/h for urban areas in Egypt
    """
    if distance_km <= 0:
        return 0
    
    time_hours = distance_km / avg_speed_kmh
    time_minutes = time_hours * 60
    
    # Add buffer time for traffic and preparation
    buffer_minutes = min(15, distance_km * 2)  # 2 minutes per km, max 15 minutes
    
    return int(time_minutes + buffer_minutes)

def get_governorate_bounds(governorate_name: str) -> dict:
    """
    Get approximate bounds for major Egyptian governorates
    Returns dict with center coordinates and radius
    """
    governorate_data = {
        'cairo': {
            'center_lat': 30.0444,
            'center_lon': 31.2357,
            'radius_km': 25
        },
        'giza': {
            'center_lat': 30.0131,
            'center_lon': 31.2089,
            'radius_km': 30
        },
        'alexandria': {
            'center_lat': 31.2001,
            'center_lon': 29.9187,
            'radius_km': 35
        },
        'qalyubia': {
            'center_lat': 30.1792,
            'center_lon': 31.2045,
            'radius_km': 40
        },
        'port_said': {
            'center_lat': 31.2653,
            'center_lon': 32.3019,
            'radius_km': 20
        },
        'suez': {
            'center_lat': 29.9668,
            'center_lon': 32.5498,
            'radius_km': 25
        },
        'ismailia': {
            'center_lat': 30.5965,
            'center_lon': 32.2715,
            'radius_km': 30
        },
        'dakahlia': {
            'center_lat': 31.0409,
            'center_lon': 31.3785,
            'radius_km': 45
        },
        'sharqia': {
            'center_lat': 30.5965,
            'center_lon': 31.5041,
            'radius_km': 50
        },
        'gharbia': {
            'center_lat': 30.8754,
            'center_lon': 31.0335,
            'radius_km': 35
        }
    }
    
    return governorate_data.get(governorate_name.lower(), {
        'center_lat': 30.0444,
        'center_lon': 31.2357,
        'radius_km': 50
    })

def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate if coordinates are within Egypt's approximate bounds
    Egypt bounds: Lat 22-32, Lon 25-35
    """
    return (22.0 <= latitude <= 32.0) and (25.0 <= longitude <= 35.0)


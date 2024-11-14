from geopy.distance import geodesic
from geopy.geocoders import Nominatim

def get_country_from_city(city):
    """Extract country from city string or return None."""
    if ',' in city:
        return city.split(',')[-1].strip()
    return None

def are_cities_on_same_continent(loc1, loc2):
    """Check if two locations are on the same continent using coordinates."""
    # Rough continent boundaries
    continents = {
        'Europe': {'min_lat': 35, 'max_lat': 71, 'min_lon': -10, 'max_lon': 40},
        'North_America': {'min_lat': 15, 'max_lat': 72, 'min_lon': -168, 'max_lon': -52},
        'Asia': {'min_lat': -10, 'max_lat': 77, 'min_lon': 40, 'max_lon': 180},
    }
    
    def get_continent(lat, lon):
        for continent, bounds in continents.items():
            if (bounds['min_lat'] <= lat <= bounds['max_lat'] and 
                bounds['min_lon'] <= lon <= bounds['max_lon']):
                return continent
        return None

    if not (loc1 and loc2 and hasattr(loc1, 'latitude') and hasattr(loc2, 'latitude')):
        return False

    cont1 = get_continent(float(loc1.latitude), float(loc1.longitude))
    cont2 = get_continent(float(loc2.latitude), float(loc2.longitude))
    
    return cont1 == cont2 and cont1 is not None

def calculate_distance(city1, city2):
    """Calculate distance between two cities using GeoPy."""
    geolocator = Nominatim(user_agent="eco_calculator")
    
    try:
        # Synchronously get locations
        loc1 = geolocator.geocode(city1, timeout=10)
        loc2 = geolocator.geocode(city2, timeout=10)
        
        if loc1 and loc2 and hasattr(loc1, 'latitude') and hasattr(loc2, 'latitude'):
            distance = geodesic(
                (loc1.latitude, loc1.longitude),
                (loc2.latitude, loc2.longitude)
            ).kilometers
            return distance, (loc1.latitude, loc1.longitude), (loc2.latitude, loc2.longitude), loc1, loc2
    except Exception as e:
        print(f"Error calculating distance: {e}")
        return None, None, None, None, None
    
    return None, None, None, None, None

def get_valid_transport_modes(distance, loc1, loc2):
    """Determine valid transport modes based on distance and geography."""
    valid_modes = []
    
    if not all([distance, loc1, loc2]):
        return ['car', 'train', 'plane']  # Default if we can't determine
    
    # Walking distance (under 5km)
    if distance <= 5:
        valid_modes.append('walk')
    
    # Bicycle distance (under 30km)
    if distance <= 30:
        valid_modes.append('bicycle')
    
    # Car and train restrictions
    same_continent = are_cities_on_same_continent(loc1, loc2)
    
    # Car (up to 1000km on same continent)
    if distance <= 1000 and same_continent:
        valid_modes.append('car')
    
    # Train (up to 2000km on same continent)
    if distance <= 2000 and same_continent:
        valid_modes.append('train')
    
    # Plane (over 100km)
    if distance > 100:
        valid_modes.append('plane')
    
    return valid_modes

def calculate_emissions(distance, transport_type):
    """Calculate CO2 emissions based on transport type and distance."""
    # Emission factors in kg CO2 per passenger per km
    emission_factors = {
        'plane': 0.255,  # Short-haul flight
        'car': 0.171,    # Average car
        'train': 0.041,  # Electric train
        'bicycle': 0,    # No emissions
        'walk': 0        # No emissions
    }
    
    if distance and transport_type in emission_factors:
        emissions = distance * emission_factors[transport_type]
        return round(emissions, 2)
    return 0

def get_transport_comparison(distance, loc1=None, loc2=None):
    """Get emissions comparison for valid transport types."""
    if distance:
        valid_modes = get_valid_transport_modes(distance, loc1, loc2)
        return {
            mode: calculate_emissions(distance, mode)
            for mode in valid_modes
        }
    return None

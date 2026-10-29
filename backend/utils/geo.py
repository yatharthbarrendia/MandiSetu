import math
from typing import Tuple, Dict

# Known coordinates for prominent agricultural hubs and mandis in Maharashtra
MAHARASHTRA_DISTRICT_COORDS: Dict[str, Tuple[float, float]] = {
    "Nashik": (19.9975, 73.7898),
    "Lasalgaon": (20.1472, 74.2267),
    "Pune": (18.5204, 73.8567),
    "Vashi": (19.0771, 72.9986),
    "Mumbai": (19.0760, 72.8777),
    "Kolhapur": (16.7050, 74.2433),
    "Solapur": (17.6599, 75.9064),
    "Ahmednagar": (19.0948, 74.7480),
    "Nagpur": (21.1458, 79.0882),
    "Jalgaon": (21.0077, 75.5626),
    "Chhatrapati Sambhajinagar": (19.8762, 75.3433),
    "Aurangabad": (19.8762, 75.3433),
    "Amravati": (20.9374, 77.7796),
    "Sangli": (16.8524, 74.5815),
    "Baramati": (18.1519, 74.5772),
}

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points on the Earth in kilometers."""
    R = 6371.0 # Earth's radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    distance = R * c
    return round(distance, 2)

def estimate_road_distance(lat1: float, lon1: float, lat2: float, lon2: float, road_factor: float = 1.25) -> float:
    """Estimate actual driving/road distance by applying a terrain and highway curvature factor (default 1.25x)."""
    aerial = haversine_distance(lat1, lon1, lat2, lon2)
    return round(aerial * road_factor, 2)

def get_location_coords(location_name: str) -> Tuple[float, float]:
    """Retrieve approximate coordinates for a known Maharashtra location or return central Maharashtra default."""
    for key, coords in MAHARASHTRA_DISTRICT_COORDS.items():
        if key.lower() in location_name.lower():
            return coords
    # Default centroid near Pune/Ahmednagar if not explicitly matched
    return (19.0, 74.5)

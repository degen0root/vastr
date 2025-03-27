from datetime import datetime, timedelta, timezone
import logging
from typing import Dict, Any
from utils.astronomy import get_sun_moon_positions, datetime_to_jd, jd_to_datetime
import swisseph as swe

logger = logging.getLogger(__name__)

# Each tithi spans 12° (360° / 30 tithis)
TITHI_SPAN = 12

# Tithi information
TITHI_INFO = {
    1: "Pratipada",
    2: "Dwitiya",
    3: "Tritiya",
    4: "Chaturthi",
    5: "Panchami",
    6: "Shashthi",
    7: "Saptami",
    8: "Ashtami",
    9: "Navami",
    10: "Dashami",
    11: "Ekadashi",
    12: "Dwadashi",
    13: "Trayodashi",
    14: "Chaturdashi",
    15: "Purnima",
    16: "Pratipada",
    17: "Dwitiya",
    18: "Tritiya",
    19: "Chaturthi",
    20: "Panchami",
    21: "Shashthi",
    22: "Saptami",
    23: "Ashtami",
    24: "Navami",
    25: "Dashami",
    26: "Ekadashi",
    27: "Dwadashi",
    28: "Trayodashi",
    29: "Chaturdashi",
    30: "Amavasya"
}

def get_lunar_phase(dt: datetime, lat: float, lon: float) -> float:
    """
    Calculate lunar phase using positions from astronomy utils.
    Phase is purely based on longitudinal difference between Moon and Sun.
    
    Args:
        dt (datetime): Date and time (UTC)
        lat (float): Latitude
        lon (float): Longitude
    
    Returns:
        float: Lunar phase in degrees (0-360)
    """
    logger.debug(f"=== Starting lunar phase calculation ===")
    logger.debug(f"Input datetime (UTC): {dt}")
    
    sun_pos, moon_pos = get_sun_moon_positions(dt, lat, lon)
    sun_lon = sun_pos["longitude"]
    moon_lon = moon_pos["longitude"]
    
    logger.debug(f"Sun longitude: {sun_lon}°")
    logger.debug(f"Moon longitude: {moon_lon}°")
    
    # Pure longitudinal difference for tithi calculation
    phase = (moon_lon - sun_lon) % 360
    logger.debug(f"Lunar phase: {phase}°")
    
    logger.debug(f"=== Lunar phase calculation complete ===")
    return phase

def find_tithi_boundary(dt: datetime, lat: float, lon: float, target_diff: float) -> datetime:
    """Find the exact time when Moon-Sun longitude difference equals target_diff.
    
    Args:
        dt (datetime): Starting datetime (UTC)
        lat (float): Latitude
        lon (float): Longitude
        target_diff (float): Target Moon-Sun longitude difference in degrees
        
    Returns:
        datetime: Time when Moon-Sun difference equals target_diff
    """
    jd_et, _ = datetime_to_jd(dt)
    
    # Get current difference to determine search direction
    sun_pos, moon_pos = get_sun_moon_positions(dt, lat, lon)
    current_diff = (moon_pos["longitude"] - sun_pos["longitude"]) % 360
    
    # Determine search window based on current position
    diff_to_target = (target_diff - current_diff) % 360
    if diff_to_target > 180:
        diff_to_target -= 360
    
    # Moon moves ~13.2° per day relative to Sun
    days_to_target = abs(diff_to_target / 13.2)
    search_window = max(0.5, min(1, days_to_target * 1.5))  # At least 0.5 days, at most 1 day
    
    if diff_to_target > 0:
        left = jd_et
        right = jd_et + search_window
    else:
        left = jd_et - search_window
        right = jd_et
    
    for _ in range(32):
        mid = (left + right) / 2
        mid_dt = jd_to_datetime(mid)
        
        sun_pos, moon_pos = get_sun_moon_positions(mid_dt, lat, lon)
        current_diff = (moon_pos["longitude"] - sun_pos["longitude"]) % 360
        
        if abs(current_diff - target_diff) < 1e-8:
            return mid_dt
            
        if current_diff < target_diff:
            left = mid
        else:
            right = mid
            
    return jd_to_datetime(right)

def calculate_tithi(dt: datetime, lat: float, lon: float) -> dict:
    """Calculate tithi for given datetime and location.
    
    Args:
        dt (datetime): Input datetime (UTC)
        lat (float): Latitude
        lon (float): Longitude
        
    Returns:
        dict: Tithi information including number, name, and boundaries
    """
    try:
        # Ensure input datetime is UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        elif dt.tzinfo != timezone.utc:
            dt = dt.astimezone(timezone.utc)
        
        # Get current Moon-Sun longitude difference
        sun_pos, moon_pos = get_sun_moon_positions(dt, lat, lon)
        moon_sun_diff = (moon_pos["longitude"] - sun_pos["longitude"]) % 360
        
        # Calculate tithi number (1-30)
        tithi_number = int(moon_sun_diff / TITHI_SPAN) + 1
        if tithi_number > 30:
            tithi_number = 30
            
        # Get tithi name
        tithi_name = TITHI_INFO[tithi_number]
        
        # Calculate tithi boundaries
        tithi_start_diff = (tithi_number - 1) * TITHI_SPAN
        tithi_end_diff = tithi_number * TITHI_SPAN
        
        # Find exact times when moon-sun difference crosses tithi boundaries
        start_time = find_tithi_boundary(dt, lat, lon, tithi_start_diff)
        end_time = find_tithi_boundary(dt, lat, lon, tithi_end_diff)
        
        result = {
            "number": tithi_number,
            "name": tithi_name,
            "start": start_time.isoformat(),
            "end": end_time.isoformat()
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating tithi: {str(e)}")
        raise 
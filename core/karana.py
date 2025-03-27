from datetime import datetime, timedelta, timezone
import logging
from typing import Dict, Any
from utils.astronomy import get_sun_moon_positions, datetime_to_jd, jd_to_datetime
from core.tithi import calculate_tithi

logger = logging.getLogger(__name__)

# Each karana spans 6° (half of tithi)
KARANA_SPAN = 6

# Karana information - first 7 are movable (Chara), last 4 are fixed (Sthira)
KARANA_INFO = {
    1: "Bava",
    2: "Balava",
    3: "Kaulava",
    4: "Taitila",
    5: "Gara",
    6: "Vanija",
    7: "Vishti",  # Also known as Bhadra
    8: "Shakuni",  # Fixed karana
    9: "Chatushpada",  # Fixed karana
    10: "Naga",  # Fixed karana
    11: "Kimstughna"  # Fixed karana
}

def find_karana_boundary(dt: datetime, lat: float, lon: float, target_diff: float) -> datetime:
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

def get_karana_number(moon_sun_diff: float, tithi_number: int) -> int:
    """Calculate karana number (1-11) from difference of Moon and Sun longitudes.
    
    Args:
        moon_sun_diff (float): Difference between Moon and Sun longitudes in degrees
        tithi_number (int): Current tithi number (1-30)
        
    Returns:
        int: Karana number (1-11)
    """
    # For fixed karanas (8-11), they only appear on specific tithis
    if tithi_number in [14, 29]:  # Chaturdashi in Krishna Paksha
        # The second half of these tithis has Shakuni karana
        if moon_sun_diff % 12 < 6:  # First half of tithi
            return 6  # Vanija
        else:  # Second half of tithi
            return 8  # Shakuni
    elif tithi_number == 30:  # Amavasya
        # The second half of Amavasya has Naga karana
        if moon_sun_diff % 12 < 6:  # First half of tithi
            return 9  # Chatushpada
        else:  # Second half of tithi
            return 10  # Naga
    elif tithi_number == 15:  # Purnima
        # The first half of Purnima has Kimstughna karana
        if moon_sun_diff % 12 < 6:  # First half of tithi
            return 11  # Kimstughna
        else:  # Second half of tithi
            return 1  # Bava
    
    # For movable karanas (1-7), calculate based on position in cycle
    # First 7 karanas repeat in a cycle of 8 tithis
    cycle_position = int(moon_sun_diff / KARANA_SPAN) % 14  # 14 half-tithis = 7 full tithis
    karana = (cycle_position % 7) + 1  # Map to 1-7
    
    return karana

def calculate_karana(dt: datetime, lat: float, lon: float) -> dict:
    """Calculate karana for given datetime and location.
    
    Args:
        dt (datetime): Input datetime (UTC)
        lat (float): Latitude
        lon (float): Longitude
        
    Returns:
        dict: Karana information including number, name, and boundaries
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
        
        # Get tithi information
        tithi_info = calculate_tithi(dt, lat, lon)
        tithi_number = tithi_info["number"]
        tithi_start = datetime.strptime(tithi_info["start"], "%Y-%m-%dT%H:%M:%S.%f+00:00").replace(tzinfo=timezone.utc)
        tithi_end = datetime.strptime(tithi_info["end"], "%Y-%m-%dT%H:%M:%S.%f+00:00").replace(tzinfo=timezone.utc)
        
        # Get karana number and name
        karana_num = get_karana_number(moon_sun_diff, tithi_number)
        karana_info = KARANA_INFO[karana_num]
        
        # Calculate exact karana boundaries based on astronomical positions
        if moon_sun_diff % 12 < 6:  # First half of tithi
            start_time = tithi_start
            # Find exact time when moon-sun difference crosses 6°
            end_time = find_karana_boundary(dt, lat, lon, (int(moon_sun_diff / 12) * 12) + 6)
        else:  # Second half of tithi
            # Find exact time when moon-sun difference crosses 6°
            start_time = find_karana_boundary(dt, lat, lon, (int(moon_sun_diff / 12) * 12) + 6)
            end_time = tithi_end
        
        result = {
            "number": karana_num,
            "name": karana_info,
            "start": start_time.isoformat(),
            "end": end_time.isoformat()
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating karana: {str(e)}")
        raise 
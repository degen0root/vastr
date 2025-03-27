from datetime import datetime, timedelta, timezone
import logging
from typing import Dict, Any
from utils.astronomy import get_sun_moon_positions, datetime_to_jd, jd_to_datetime
from core.tithi import calculate_tithi

logger = logging.getLogger(__name__)

# Each karana spans 6° (half of tithi)
KARANA_SPAN = 6

# Karana information
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

# Degree-based karana mapping for each tithi half
# Format: (tithi_number, is_second_half): (karana_number, degree_start, degree_end)
KARANA_DEGREE_MAP = {
    # Shukla Paksha
    (1, False): (11, 0, 6),      # Kimstughna
    (1, True): (1, 6, 12),       # Bava
    (2, False): (3, 12, 18),     # Kaulava
    (2, True): (4, 18, 24),      # Taitila
    (3, False): (5, 24, 30),     # Gara
    (3, True): (6, 30, 36),      # Vanija
    (4, False): (7, 36, 42),     # Vishti
    (4, True): (8, 42, 48),      # Shakuni
    (5, False): (9, 48, 54),     # Chatushpada
    (5, True): (10, 54, 60),     # Naga
    (6, False): (11, 60, 66),    # Kimstughna
    (6, True): (1, 66, 72),      # Bava
    (7, False): (3, 72, 78),     # Kaulava
    (7, True): (4, 78, 84),      # Taitila
    (8, False): (5, 84, 90),     # Gara
    (8, True): (6, 90, 96),      # Vanija
    (9, False): (7, 96, 102),    # Vishti
    (9, True): (8, 102, 108),    # Shakuni
    (10, False): (9, 108, 114),  # Chatushpada
    (10, True): (10, 114, 120),  # Naga
    (11, False): (11, 120, 126), # Kimstughna
    (11, True): (1, 126, 132),   # Bava
    (12, False): (3, 132, 138),  # Kaulava
    (12, True): (4, 138, 144),   # Taitila
    (13, False): (5, 144, 150),  # Gara
    (13, True): (6, 150, 156),   # Vanija
    (14, False): (7, 156, 162),  # Vishti
    (14, True): (8, 162, 168),   # Shakuni
    (15, False): (9, 168, 174),  # Chatushpada (Purnima)
    (15, True): (10, 174, 180),  # Naga (Purnima)
    
    # Krishna Paksha
    (16, False): (11, 180, 186), # Kimstughna
    (16, True): (1, 186, 192),   # Bava
    (17, False): (3, 192, 198),  # Kaulava
    (17, True): (4, 198, 204),   # Taitila
    (18, False): (5, 204, 210),  # Gara
    (18, True): (6, 210, 216),   # Vanija
    (19, False): (7, 216, 222),  # Vishti
    (19, True): (8, 222, 228),   # Shakuni
    (20, False): (9, 228, 234),  # Chatushpada
    (20, True): (10, 234, 240),  # Naga
    (21, False): (11, 240, 246), # Kimstughna
    (21, True): (1, 246, 252),   # Bava
    (22, False): (3, 252, 258),  # Kaulava
    (22, True): (4, 258, 264),   # Taitila
    (23, False): (5, 264, 270),  # Gara
    (23, True): (6, 270, 276),   # Vanija
    (24, False): (7, 276, 282),  # Vishti
    (24, True): (8, 282, 288),   # Shakuni
    (25, False): (9, 288, 294),  # Chatushpada
    (25, True): (10, 294, 300),  # Naga
    (26, False): (11, 300, 306), # Kimstughna
    (26, True): (1, 306, 312),   # Bava
    (27, False): (3, 312, 318),  # Kaulava
    (27, True): (4, 318, 324),   # Taitila
    (28, False): (5, 324, 330),  # Gara
    (28, True): (6, 330, 336),   # Vanija
    (29, False): (7, 336, 342),  # Vishti
    (29, True): (8, 342, 348),   # Shakuni
    (30, False): (9, 348, 354),  # Chatushpada (Amavasya)
    (30, True): (10, 354, 360),  # Naga (Amavasya)
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
    """
    Calculate karana number based on Moon-Sun angle and tithi number.
    
    Args:
        moon_sun_diff (float): Difference between Moon and Sun longitudes in degrees
        tithi_number (int): Current tithi number (1-30)
        
    Returns:
        int: Karana number (1-11)
    """
    # Determine if we're in first or second half of tithi
    is_second_half = (moon_sun_diff % 12) >= 6
    
    # Get karana info from degree map
    karana_info = KARANA_DEGREE_MAP.get((tithi_number, is_second_half))
    if karana_info is None:
        logger.error(f"No karana mapping found for tithi {tithi_number}, is_second_half {is_second_half}")
        return 1  # Default to Bava if mapping not found
    
    karana_number, degree_start, degree_end = karana_info
    logger.debug(f"Karana mapping: tithi={tithi_number}, half={'second' if is_second_half else 'first'}, "
                f"karana={karana_number}, degrees={degree_start}-{degree_end}")
    
    return karana_number

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
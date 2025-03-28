from datetime import datetime, timedelta, timezone
import logging
from typing import Dict, Any
from utils.astronomy import get_sun_moon_positions, datetime_to_jd, jd_to_datetime
import swisseph as swe

logger = logging.getLogger(__name__)

# Each nakshatra spans 13°20' (13.3333... degrees)
NAKSHATRA_SPAN = 360 / 27

# Nakshatra information
NAKSHATRA_INFO = {
    1: {"name": "Ashwini", "favorable": "Neutral"},  # Fast-acting, good for healing but impulsive
    2: {"name": "Bharani", "favorable": "Unfavorable"},  # Harsh, associated with transformation
    3: {"name": "Krittika", "favorable": "Unfavorable"},  # Sharp & burning, can cause disputes
    4: {"name": "Rohini", "favorable": "Favorable"},  # Best for stability, marriage, and property
    5: {"name": "Mrigashira", "favorable": "Favorable"},  # Good for creativity, travel, and new ventures
    6: {"name": "Ardra", "favorable": "Unfavorable"},  # Destructive, linked to storms and struggles
    7: {"name": "Punarvasu", "favorable": "Neutral"},  # Good for learning but may delay results
    8: {"name": "Pushya", "favorable": "Favorable"},  # Highly auspicious (best for rituals, business, and education)
    9: {"name": "Ashlesha", "favorable": "Unfavorable"},  # Deceptive, associated with poison
    10: {"name": "Magha", "favorable": "Unfavorable"},  # Ego clashes, best for ancestral rituals
    11: {"name": "Purva Phalguni", "favorable": "Unfavorable"},  # Excess indulgence, risky for commitments
    12: {"name": "Uttara Phalguni", "favorable": "Favorable"},  # Good for marriage, career, and long-term plans
    13: {"name": "Hasta", "favorable": "Favorable"},  # Good for skills, arts, and financial gains
    14: {"name": "Chitra", "favorable": "Neutral"},  # Neutral status
    15: {"name": "Swati", "favorable": "Favorable"},  # Favorable for trade, diplomacy, and new beginnings
    16: {"name": "Vishakha", "favorable": "Neutral"},  # Strong for goals but can bring conflicts
    17: {"name": "Anuradha", "favorable": "Favorable"},  # Supports teamwork, love, and spiritual growth
    18: {"name": "Jyeshtha", "favorable": "Unfavorable"},  # Competitive, can bring power struggles
    19: {"name": "Mula", "favorable": "Unfavorable"},  # Destructive, good for endings, not beginnings
    20: {"name": "Purva Ashadha", "favorable": "Unfavorable"},  # Conflict-prone, aggressive energy
    21: {"name": "Uttara Ashadha", "favorable": "Favorable"},  # Brings success in competitions and leadership
    22: {"name": "Shravana", "favorable": "Neutral"},  # Good for learning but sensitive to malefic influences
    23: {"name": "Dhanishta", "favorable": "Neutral"},  # Neutral status
    24: {"name": "Shatabhisha", "favorable": "Neutral"},  # Neutral status
    25: {"name": "Purva Bhadrapada", "favorable": "Neutral"},  # Neutral status
    26: {"name": "Uttara Bhadrapada", "favorable": "Neutral"},  # Neutral status
    27: {"name": "Revati", "favorable": "Favorable"}  # Auspicious for journeys, charity, and blessings
}

# Constellation information for each nakshatra
CONSTELLATION_INFO = {
    1: "Aries",
    2: "Aries",
    3: "Taurus",
    4: "Taurus",
    5: "Taurus",
    6: "Gemini",
    7: "Gemini",
    8: "Cancer",
    9: "Cancer",
    10: "Leo",
    11: "Leo",
    12: "Leo",
    13: "Virgo",
    14: "Virgo",
    15: "Libra",
    16: "Libra",
    17: "Scorpio",
    18: "Scorpio",
    19: "Sagittarius",
    20: "Sagittarius",
    21: "Capricorn",
    22: "Capricorn",
    23: "Aquarius",
    24: "Aquarius",
    25: "Pisces",
    26: "Pisces",
    27: "Pisces"
}

def get_nakshatra_number(moon_longitude: float) -> int:
    """
    Calculate nakshatra number (1-27) from Moon's longitude.
    
    Args:
        moon_longitude (float): Moon's longitude in degrees (0-360)
        
    Returns:
        int: Nakshatra number (1-27)
    """
    # Each nakshatra spans 13°20' (13.3333... degrees)
    nakshatra = int(moon_longitude / NAKSHATRA_SPAN) + 1
    return nakshatra

def find_nakshatra_boundary(dt: datetime, lat: float, lon: float, nakshatra: int, direction: int, recursion_depth: int = 0) -> datetime:
    """
    Find the exact boundary of a nakshatra based on traditional Vedic astrology principles.
    Each nakshatra spans exactly 13°20' (13.3333... degrees).
    
    Args:
        dt (datetime): Starting datetime (UTC)
        lat (float): Latitude
        lon (float): Longitude
        nakshatra (int): Nakshatra number (1-27)
        direction (int): Search direction (-1 for start, 1 for end)
        recursion_depth (int): Current recursion depth (for safety)
    
    Returns:
        datetime: The datetime of the nakshatra boundary
    """
    if recursion_depth >= 3:
        logger.warning("Maximum recursion depth reached, returning best estimate")
        return dt

    logger.debug(f"Searching {'end' if direction == 1 else 'start'} of Nakshatra {nakshatra}")

    # Convert input time to JD (UT)
    _, jd_ut = datetime_to_jd(dt)

    # Calculate target longitude based on traditional Vedic astrology
    # Each nakshatra spans exactly 13°20' (13.3333... degrees)
    if direction == 1:  # End boundary
        target_lon = (nakshatra * NAKSHATRA_SPAN) % 360
    else:  # Start boundary
        target_lon = ((nakshatra - 1) * NAKSHATRA_SPAN) % 360

    # Get Moon's current position
    _, moon_pos = get_sun_moon_positions(dt, lat, lon)
    current_lon = moon_pos["longitude"]
    
    # Initialize search window based on Moon's average daily motion (13.2 degrees/day)
    # This helps ensure we capture the boundary within our search window
    moon_daily_motion = 13.2
    time_to_boundary = abs(((current_lon - target_lon + 180) % 360 - 180) / moon_daily_motion)
    
    if direction == 1:  # Searching forward for end
        if current_lon > target_lon:
            target_lon += 360  # Look for next occurrence
        left = jd_ut - 0.2  # Start searching from slightly before
        right = jd_ut + time_to_boundary + 1.0  # Add buffer
    else:  # Searching backward for start
        if current_lon < target_lon:
            target_lon -= 360  # Look for previous occurrence
        left = jd_ut - time_to_boundary - 1.0  # Add buffer
        right = jd_ut + 0.2  # Search slightly ahead

    # Binary search with high precision
    best_diff = float('inf')
    best_jd = None
    
    for i in range(60):  # Increased iterations for better precision
        mid = (left + right) / 2
        mid_dt = jd_to_datetime(mid)
        _, moon_pos = get_sun_moon_positions(mid_dt, lat, lon)
        current_lon = moon_pos["longitude"]

        # Normalize longitude difference for comparison
        lon_diff = (current_lon - target_lon + 180) % 360 - 180
        
        # Keep track of best result
        if abs(lon_diff) < abs(best_diff):
            best_diff = lon_diff
            best_jd = mid

        if abs(lon_diff) < 0.0001:  # Found exact boundary (within 0.36 arc-seconds)
            break

        if (direction == 1 and lon_diff >= 0) or (direction == -1 and lon_diff <= 0):
            right = mid
        else:
            left = mid

    # Use the best result found
    boundary_dt = jd_to_datetime(best_jd if best_jd is not None else right)
    
    # Verify both before and after the boundary
    verify_before = boundary_dt - timedelta(minutes=30)  # Increased verification window
    verify_after = boundary_dt + timedelta(minutes=30)
    
    _, pos_before = get_sun_moon_positions(verify_before, lat, lon)
    _, pos_at = get_sun_moon_positions(boundary_dt, lat, lon)
    _, pos_after = get_sun_moon_positions(verify_after, lat, lon)
    
    lon_before = pos_before["longitude"]
    lon_at = pos_at["longitude"]
    lon_after = pos_after["longitude"]
    
    # Normalize differences for comparison
    diff_before = (lon_before - target_lon + 180) % 360 - 180
    diff_at = (lon_at - target_lon + 180) % 360 - 180
    diff_after = (lon_after - target_lon + 180) % 360 - 180

    # Verify the boundary transition is correct
    if direction == 1:  # End boundary
        if diff_before > 0 or diff_after < 0 or abs(diff_at) > 0.01:
            logger.warning(f"End boundary verification failed (before: {diff_before}°, at: {diff_at}°, after: {diff_after}°)")
            new_dt = boundary_dt + timedelta(hours=2)  # Increased adjustment
            return find_nakshatra_boundary(new_dt, lat, lon, nakshatra, direction, recursion_depth + 1)
    else:  # Start boundary
        if diff_before < 0 or diff_after > 0 or abs(diff_at) > 0.01:
            logger.warning(f"Start boundary verification failed (before: {diff_before}°, at: {diff_at}°, after: {diff_after}°)")
            new_dt = boundary_dt - timedelta(hours=2)  # Increased adjustment
            return find_nakshatra_boundary(new_dt, lat, lon, nakshatra, direction, recursion_depth + 1)

    return boundary_dt

def calculate_nakshatra(dt: datetime, lat: float, lon: float) -> dict:
    """
    Calculate nakshatra for given datetime and location.
    
    Args:
        dt (datetime): Input datetime (UTC)
        lat (float): Latitude
        lon (float): Longitude
        
    Returns:
        dict: Nakshatra information including number, name, favorable status, constellation, and boundaries
    """
    try:
        logger.debug(f"=== Starting nakshatra calculation ===")
        logger.debug(f"Input parameters - DateTime (UTC): {dt}, Lat: {lat}, Lon: {lon}")
        
        # Ensure input datetime is UTC
        if dt.tzinfo is None:
            logger.warning("Input datetime has no timezone, assuming UTC")
            dt = dt.replace(tzinfo=timezone.utc)
        elif dt.tzinfo != timezone.utc:
            dt = dt.astimezone(timezone.utc)
            logger.info(f"Converted input datetime to UTC: {dt}")
        
        # Get Moon's position
        _, moon_pos = get_sun_moon_positions(dt, lat, lon)
        moon_longitude = moon_pos["longitude"]
        
        # Calculate nakshatra number
        nakshatra_num = get_nakshatra_number(moon_longitude)
        logger.debug(f"Calculated nakshatra number: {nakshatra_num}")
        
        # Get nakshatra information
        nakshatra_info = NAKSHATRA_INFO[nakshatra_num]
        nakshatra_name = nakshatra_info["name"]
        nakshatra_favorable = nakshatra_info["favorable"]
        
        # Get constellation information
        constellation = CONSTELLATION_INFO[nakshatra_num]
        
        # Find end time of current nakshatra
        end_time = find_nakshatra_boundary(dt, lat, lon, nakshatra_num, 1)
        
        # Find start time by finding end time of previous nakshatra
        prev_nakshatra = nakshatra_num - 1 if nakshatra_num > 1 else 27
        start_time = find_nakshatra_boundary(end_time - timedelta(days=1), lat, lon, prev_nakshatra, 1)
        
        # Validate duration (nakshatras typically last between 22-26 hours)
        duration = (end_time - start_time).total_seconds()
        if duration < 20 * 3600 or duration > 28 * 3600:  # Between 20 and 28 hours
            logger.warning(f"Unusual nakshatra duration: {duration/3600:.2f} hours")
        
        logger.debug(f"Nakshatra duration: {duration/3600:.2f} hours")
        
        result = {
            "number": nakshatra_num,
            "name": nakshatra_name,
            "favorable": nakshatra_favorable,
            "constellation": constellation,
            "start": start_time.isoformat(),
            "end": end_time.isoformat()
        }
        
        logger.debug(f"=== Nakshatra calculation complete ===")
        logger.debug(f"Final result: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating nakshatra: {str(e)}")
        raise 
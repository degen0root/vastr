from datetime import datetime, timedelta, timezone
import logging
from typing import Dict, Any
from utils.astronomy import get_sun_moon_positions, datetime_to_jd, jd_to_datetime

logger = logging.getLogger(__name__)

# Each yoga spans 27° (360° / 27)
YOGA_SPAN = 360 / 27

# Yoga information
YOGA_INFO = {
    1: {"name": "Vishkambha", "favorable": "Unfavorable"},  # Obstacles & delays
    2: {"name": "Priti", "favorable": "Favorable"},  # Love and harmony
    3: {"name": "Ayushman", "favorable": "Favorable"},  # Longevity and health
    4: {"name": "Saubhagya", "favorable": "Favorable"},  # Prosperity & happiness
    5: {"name": "Shobhana", "favorable": "Favorable"},  # Beauty and auspiciousness
    6: {"name": "Atiganda", "favorable": "Unfavorable"},  # Extreme dangers & conflicts
    7: {"name": "Sukarma", "favorable": "Favorable"},  # Good deeds and success
    8: {"name": "Dhriti", "favorable": "Favorable"},  # Stability and determination
    9: {"name": "Shula", "favorable": "Unfavorable"},  # Pain & suffering
    10: {"name": "Ganda", "favorable": "Favorable"},  # Only when not combined with malefic planets
    11: {"name": "Vriddhi", "favorable": "Favorable"},  # Growth and expansion
    12: {"name": "Dhruva", "favorable": "Favorable"},  # Stability & long-term gains
    13: {"name": "Vyaghata", "favorable": "Unfavorable"},  # Sudden destruction
    14: {"name": "Harshana", "favorable": "Favorable"},  # Joy but short-lived results
    15: {"name": "Vajra", "favorable": "Favorable"},  # Strong but rigid (good for defense)
    16: {"name": "Siddhi", "favorable": "Favorable"},  # Success & achievements
    17: {"name": "Vyatipata", "favorable": "Favorable"},  # Risky but can be used for radical change
    18: {"name": "Variyana", "favorable": "Favorable"},  # Wealth & luxury
    19: {"name": "Parigha", "favorable": "Unfavorable"},  # Blockages & restrictions
    20: {"name": "Shiva", "favorable": "Favorable"},  # Divine blessings
    21: {"name": "Siddha", "favorable": "Favorable"},  # Success & achievements
    22: {"name": "Sadhya", "favorable": "Favorable"},  # Accomplishment
    23: {"name": "Shubha", "favorable": "Favorable"},  # General auspiciousness
    24: {"name": "Shukla", "favorable": "Favorable"},  # Purity and clarity
    25: {"name": "Brahma", "favorable": "Favorable"},  # Divine wisdom
    26: {"name": "Indra", "favorable": "Favorable"},  # Leadership and power
    27: {"name": "Vaidhriti", "favorable": "Unfavorable"}  # Bhadra Yoga - Deceptive outcomes
}

def get_yoga_number(sun_longitude: float, moon_longitude: float) -> int:
    """
    Calculate yoga number (1-27) from sum of Sun and Moon longitudes.
    
    Args:
        sun_longitude (float): Sun's longitude in degrees (0-360)
        moon_longitude (float): Moon's longitude in degrees (0-360)
        
    Returns:
        int: Yoga number (1-27)
    """
    # Yoga is determined by the sum of Sun and Moon longitudes
    total_longitude = (sun_longitude + moon_longitude) % 360
    yoga = int(total_longitude / YOGA_SPAN) + 1
    return yoga

def find_yoga_boundary(dt: datetime, lat: float, lon: float, yoga: int, direction: int, recursion_depth: int = 0) -> datetime:
    """
    Find the exact boundary of a yoga based on traditional Vedic astrology principles.
    Each yoga spans exactly 13°20' (13.3333... degrees).
    
    Args:
        dt (datetime): Starting datetime (UTC)
        lat (float): Latitude
        lon (float): Longitude
        yoga (int): Yoga number (1-27)
        direction (int): Search direction (-1 for start, 1 for end)
        recursion_depth (int): Current recursion depth (for safety)
    
    Returns:
        datetime: The datetime of the yoga boundary
    """
    if recursion_depth >= 3:
        logger.warning("Maximum recursion depth reached, returning best estimate")
        return dt

    logger.debug(f"Searching {'end' if direction == 1 else 'start'} of Yoga {yoga}")

    # Convert input time to JD (UT)
    _, jd_ut = datetime_to_jd(dt)

    # Calculate target total longitude based on traditional Vedic astrology
    if direction == 1:  # End boundary
        target_total = (yoga * YOGA_SPAN) % 360
    else:  # Start boundary
        target_total = ((yoga - 1) * YOGA_SPAN) % 360

    # Get current positions
    sun_pos, moon_pos = get_sun_moon_positions(dt, lat, lon)
    current_total = (sun_pos["longitude"] + moon_pos["longitude"]) % 360
    
    # Initialize search window based on average daily motion
    # Sun moves ~1° per day, Moon ~13.2° per day, so total motion is ~14.2° per day
    total_daily_motion = 14.2
    time_to_boundary = abs(((current_total - target_total + 180) % 360 - 180) / total_daily_motion)
    
    if direction == 1:  # Searching forward for end
        if current_total > target_total:
            target_total += 360  # Look for next occurrence
        left = jd_ut - 0.2  # Start searching from slightly before
        right = jd_ut + time_to_boundary + 1.0  # Add buffer
    else:  # Searching backward for start
        if current_total < target_total:
            target_total -= 360  # Look for previous occurrence
        left = jd_ut - time_to_boundary - 1.0  # Add buffer
        right = jd_ut + 0.2  # Search slightly ahead

    # Binary search with high precision
    best_diff = float('inf')
    best_jd = None
    
    for i in range(60):  # Increased iterations for better precision
        mid = (left + right) / 2
        mid_dt = jd_to_datetime(mid)
        sun_pos, moon_pos = get_sun_moon_positions(mid_dt, lat, lon)
        current_total = (sun_pos["longitude"] + moon_pos["longitude"]) % 360

        # Normalize longitude difference for comparison
        total_diff = (current_total - target_total + 180) % 360 - 180
        
        # Keep track of best result
        if abs(total_diff) < abs(best_diff):
            best_diff = total_diff
            best_jd = mid

        if abs(total_diff) < 0.0001:  # Found exact boundary (within 0.36 arc-seconds)
            break

        if (direction == 1 and total_diff >= 0) or (direction == -1 and total_diff <= 0):
            right = mid
        else:
            left = mid

    # Use the best result found
    boundary_dt = jd_to_datetime(best_jd if best_jd is not None else right)
    
    # Verify both before and after the boundary
    verify_before = boundary_dt - timedelta(minutes=30)  # Increased verification window
    verify_after = boundary_dt + timedelta(minutes=30)
    
    sun_before, moon_before = get_sun_moon_positions(verify_before, lat, lon)
    sun_at, moon_at = get_sun_moon_positions(boundary_dt, lat, lon)
    sun_after, moon_after = get_sun_moon_positions(verify_after, lat, lon)
    
    total_before = (sun_before["longitude"] + moon_before["longitude"]) % 360
    total_at = (sun_at["longitude"] + moon_at["longitude"]) % 360
    total_after = (sun_after["longitude"] + moon_after["longitude"]) % 360
    
    # Normalize differences for comparison
    diff_before = (total_before - target_total + 180) % 360 - 180
    diff_at = (total_at - target_total + 180) % 360 - 180
    diff_after = (total_after - target_total + 180) % 360 - 180

    # Verify the boundary transition is correct
    if direction == 1:  # End boundary
        if diff_before > 0 or diff_after < 0 or abs(diff_at) > 0.01:
            logger.warning(f"End boundary verification failed (before: {diff_before}°, at: {diff_at}°, after: {diff_after}°)")
            new_dt = boundary_dt + timedelta(hours=2)  # Increased adjustment
            return find_yoga_boundary(new_dt, lat, lon, yoga, direction, recursion_depth + 1)
    else:  # Start boundary
        if diff_before < 0 or diff_after > 0 or abs(diff_at) > 0.01:
            logger.warning(f"Start boundary verification failed (before: {diff_before}°, at: {diff_at}°, after: {diff_after}°)")
            new_dt = boundary_dt - timedelta(hours=2)  # Increased adjustment
            return find_yoga_boundary(new_dt, lat, lon, yoga, direction, recursion_depth + 1)

    return boundary_dt

def calculate_yoga(dt: datetime, lat: float, lon: float) -> dict:
    """
    Calculate yoga for given datetime and location.
    
    Args:
        dt (datetime): Input datetime (UTC)
        lat (float): Latitude
        lon (float): Longitude
        
    Returns:
        dict: Yoga information including number, name, favorable status, and boundaries
    """
    try:
        logger.debug(f"=== Starting yoga calculation ===")
        logger.debug(f"Input parameters - DateTime (UTC): {dt}, Lat: {lat}, Lon: {lon}")
        
        # Ensure input datetime is UTC
        if dt.tzinfo is None:
            logger.warning("Input datetime has no timezone, assuming UTC")
            dt = dt.replace(tzinfo=timezone.utc)
        elif dt.tzinfo != timezone.utc:
            dt = dt.astimezone(timezone.utc)
            logger.info(f"Converted input datetime to UTC: {dt}")
        
        # Get Sun and Moon positions
        sun_pos, moon_pos = get_sun_moon_positions(dt, lat, lon)
        sun_longitude = sun_pos["longitude"]
        moon_longitude = moon_pos["longitude"]
        
        # Calculate yoga number
        yoga_num = get_yoga_number(sun_longitude, moon_longitude)
        logger.debug(f"Calculated yoga number: {yoga_num}")
        
        # Get yoga information
        yoga_info = YOGA_INFO[yoga_num]
        yoga_name = yoga_info["name"]
        yoga_favorable = yoga_info["favorable"]
        
        # Find end time of current yoga
        end_time = find_yoga_boundary(dt, lat, lon, yoga_num, 1)
        
        # Find start time by finding end time of previous yoga
        prev_yoga = yoga_num - 1 if yoga_num > 1 else 27
        start_time = find_yoga_boundary(end_time - timedelta(days=1), lat, lon, prev_yoga, 1)
        
        # Validate duration (yogas typically last between 22-26 hours)
        duration = (end_time - start_time).total_seconds()
        if duration < 20 * 3600 or duration > 28 * 3600:  # Between 20 and 28 hours
            logger.warning(f"Unusual yoga duration: {duration/3600:.2f} hours")
        
        logger.debug(f"Yoga duration: {duration/3600:.2f} hours")
        
        result = {
            "number": yoga_num,
            "name": yoga_name,
            "favorable": yoga_favorable,
            "start": start_time.isoformat(),
            "end": end_time.isoformat()
        }
        
        logger.debug(f"=== Yoga calculation complete ===")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating yoga: {str(e)}")
        raise 
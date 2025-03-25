from datetime import datetime, timedelta, timezone
import logging
from typing import Dict, Any
from utils.astronomy import get_sun_moon_positions, datetime_to_jd, jd_to_datetime
import swisseph as swe

logger = logging.getLogger(__name__)

# Simplified TITHI_INFO - just numbers 1-30
TITHI_INFO = {i: {} for i in range(1, 31)}

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

def find_tithi_boundary(dt: datetime, lat: float, lon: float, tithi: int, direction: int) -> datetime:
    """
    Find exact tithi boundary using phase-targeted search.
    
    Args:
        dt (datetime): Starting datetime (UTC)
        lat (float): Latitude
        lon (float): Longitude
        tithi (int): Absolute tithi number (1-30)
        direction (int): Search direction (-1 for start, 1 for end)
    
    Returns:
        datetime: The datetime of the tithi boundary
    """
    logger.debug(f"=== Starting tithi boundary search ===")
    logger.debug(f"Search parameters - DateTime: {dt}, Tithi: {tithi}, Direction: {direction}")
    
    # Calculate target phase
    target_phase = (tithi * 12) % 360 if direction == 1 else ((tithi - 1) * 12) % 360
    logger.debug(f"Target phase: {target_phase}°")
    
    # Convert to JD and set initial search parameters
    jd_et, jd_ut = datetime_to_jd(dt)  # Get both ET and UT
    jd = jd_et  # Use ET for astronomical calculations
    step = 0.01  # Initial step (~14.4 minutes)
    max_iterations = 1000  # Prevent infinite loops
    
    logger.debug(f"Starting search from JD (ET): {jd}")
    logger.debug(f"Initial step size: {step} days")
    
    # First pass: Find approximate boundary with coarse steps
    for i in range(max_iterations):
        current_dt = jd_to_datetime(jd)  # Convert ET back to datetime
        current_phase = get_lunar_phase(current_dt, lat, lon)
        phase_diff = (current_phase - target_phase) % 360
        
        logger.debug(f"Iteration {i}: JD (ET)={jd}, Phase={current_phase}°, Diff={phase_diff}°")
        
        # Check if we've crossed the boundary
        if (direction == 1 and phase_diff < 1.0) or (direction == -1 and phase_diff > 359.0):
            # Found approximate boundary, now refine with binary search
            left = jd - step if direction == 1 else jd
            right = jd if direction == 1 else jd + step
            
            logger.debug(f"Found approximate boundary, refining between JD (ET) {left} and {right}")
            
            # Binary search for precise boundary
            prev_mid = None
            prev_phase = None
            
            for j in range(100):  # Increased from 50 to 100 iterations for refinement
                mid = (left + right) / 2
                mid_dt = jd_to_datetime(mid)  # Convert ET to datetime
                mid_phase = get_lunar_phase(mid_dt, lat, lon)
                
                logger.debug(f"Refinement {j}: JD (ET)={mid}, Phase={mid_phase}°")
                
                # Store the previous point for interpolation
                if prev_mid is None or (direction == 1 and mid_phase < target_phase) or (direction == -1 and mid_phase > target_phase):
                    prev_mid = mid
                    prev_phase = mid_phase
                
                if (direction == 1 and mid_phase >= target_phase) or (direction == -1 and mid_phase <= target_phase):
                    right = mid
                else:
                    left = mid
                
                if abs(right - left) < 1e-12:  # Increased precision from 1e-8 to 1e-12
                    break
            
            # Linear interpolation to find exact transition point
            if prev_mid is not None and prev_phase is not None:
                # Get the final two points
                point1 = (prev_mid, prev_phase)
                point2 = (right, get_lunar_phase(jd_to_datetime(right), lat, lon))
                
                # Interpolate to find exact JD where phase equals target_phase
                phase_diff = point2[1] - point1[1]
                if abs(phase_diff) > 1e-12:  # Increased precision from 1e-8 to 1e-12
                    t = (target_phase - point1[1]) / phase_diff
                    exact_jd = point1[0] + t * (point2[0] - point1[0])
                else:
                    exact_jd = point2[0]  # Use the endpoint if points are too close
                
                result_dt = jd_to_datetime(exact_jd)
            else:
                result_dt = jd_to_datetime(right)
            
            logger.debug(f"Found boundary at: {result_dt}")
            return result_dt
        
        jd += step * direction
        
        # Safety check: don't search more than 2 days
        if abs(jd - jd_et) > 2.0:  # Compare with original ET
            raise ValueError("Boundary not found within 2 days")
    
    raise ValueError("Maximum iterations reached without finding boundary")

def calculate_tithi(dt: datetime, lat: float, lon: float) -> dict:
    """
    Calculate tithi (lunar day) for given datetime and location.
    
    Args:
        dt (datetime): Input datetime (UTC)
        lat (float): Latitude
        lon (float): Longitude
        
    Returns:
        dict: Tithi information including number and boundaries
    """
    try:
        logger.debug(f"=== Starting tithi calculation ===")
        logger.debug(f"Input parameters - DateTime (UTC): {dt}, Lat: {lat}, Lon: {lon}")
        
        # Ensure input datetime is UTC
        if dt.tzinfo is None:
            logger.warning("Input datetime has no timezone, assuming UTC")
            dt = dt.replace(tzinfo=timezone.utc)
        elif dt.tzinfo != timezone.utc:
            dt = dt.astimezone(timezone.utc)
            logger.info(f"Converted input datetime to UTC: {dt}")
        
        # Calculate lunar phase
        phase = get_lunar_phase(dt, lat, lon)
        
        # Calculate tithi number (1-30)
        # Use >= for boundary comparison to properly handle exact transitions
        tithi_num = int(phase // 12) + (1 if phase % 12 >= 0 else 0)
        logger.debug(f"Calculated tithi number: {tithi_num}")
        
        # Find boundaries
        start_time = find_tithi_boundary(dt, lat, lon, tithi_num, -1)
        end_time = find_tithi_boundary(dt, lat, lon, tithi_num, 1)
        
        # Validate duration
        duration = (end_time - start_time).total_seconds()
        if duration < 19 * 3600 or duration > 27 * 3600:  # Between 19 and 27 hours
            raise ValueError(f"Invalid tithi duration: {duration/3600:.2f} hours (expected 19-27 hours)")
        
        logger.debug(f"Tithi duration: {duration/3600:.2f} hours")
        
        result = {
            "number": tithi_num,
            "start": start_time.strftime("%Y-%m-%dT%H:%M:%S.%f+00:00"),
            "end": end_time.strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
        }
        
        logger.debug(f"=== Tithi calculation complete ===")
        logger.debug(f"Final result: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in tithi calculation: {str(e)}")
        raise 
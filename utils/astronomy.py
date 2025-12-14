from datetime import datetime, timedelta
import swisseph as swe
import pytz
import logging
import requests
import json
from functools import lru_cache
from typing import Dict, Any

"""
Vedic Astronomy Utilities

This module provides astronomical calculations using the Vedic (sidereal) system.
All calculations use:
- Lahiri ayanamsa (Indian standard)
- Sidereal zodiac (fixed star-based)
- Topocentric positions (observer's location)
- Swiss Ephemeris for precise calculations

The ephemeris path must be set before using these functions (typically in main.py).
"""

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PolarDayNightError(ValueError):
    """
    Raised when there is no sunrise or sunset for the given
    date and location (polar day or polar night conditions).
    """

    pass

def setup_astronomy():
    """Setup astronomy calculations with correct ayanamsha and ephemeris."""
    # Set Lahiri ayanamsha for sidereal calculations
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    # Verify ephemeris files
    try:
        test_jd = swe.julday(2000, 1, 1, 0)
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED3  # Use Swiss Ephemeris files
        sun_res = swe.calc_ut(test_jd, swe.SUN, flags)
        if sun_res[0] == -1:  # Error occurred
            logger.warning("Swiss Ephemeris files not found, falling back to Moshier")
            flags = swe.FLG_MOSEPH | swe.FLG_SPEED3
    except Exception as e:
        logger.error(f"Error setting up astronomy: {str(e)}")
        flags = swe.FLG_MOSEPH | swe.FLG_SPEED3
    
    return flags

# Initialize astronomy settings
CALC_FLAGS = setup_astronomy()

# Cache for elevation data
_elevation_cache: Dict[str, float] = {}

def debug_swe_calc(func_name: str, jd: float, result: tuple) -> None:
    """
    Debug Swiss Ephemeris calculation results.
    
    Args:
        func_name: Name of the function being debugged
        jd: Julian day number used in calculation
        result: Result tuple from Swiss Ephemeris calculation
    """
    logger.debug(f"{func_name} calculation at JD {jd}:")
    logger.debug(f"Return flag: {result[0]}")
    logger.debug(f"Position data: {result[1]}")
    if len(result) > 2:
        logger.debug(f"Additional data: {result[2:]}")

@lru_cache(maxsize=1000)
def get_elevation(lat: float, lon: float) -> float:
    """
    Get elevation in meters for given coordinates using Open Topo Data API.
    Uses the GEBCO2020 dataset which provides global coverage with ~450m resolution.
    Implements caching to avoid repeated API calls for the same coordinates.
    
    Args:
        lat: latitude in degrees
        lon: longitude in degrees
    
    Returns:
        float: elevation in meters above sea level
    """
    try:
        # Create cache key
        cache_key = f"{lat},{lon}"
        
        # Check cache first
        if cache_key in _elevation_cache:
            logger.debug(f"Using cached elevation for lat={lat}, lon={lon}: {_elevation_cache[cache_key]}m")
            return _elevation_cache[cache_key]
        
        url = f"https://api.opentopodata.org/v1/gebco2020?locations={lat},{lon}"
        logger.debug(f"Requesting elevation data from: {url}")
        
        # Add timeout to the request
        response = requests.get(url, timeout=5)  # 5 second timeout
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = response.json()
        logger.debug(f"Elevation API response: {json.dumps(data, indent=2)}")
        
        if data["status"] == "OK" and len(data["results"]) > 0:
            elevation = data["results"][0]["elevation"]
            logger.debug(f"Elevation lookup result for lat={lat}, lon={lon}: {elevation}m")
            # Cache the result
            _elevation_cache[cache_key] = float(elevation)
            return float(elevation)
        else:
            logger.warning(f"No elevation data found for lat={lat}, lon={lon}. Using 0m as fallback.")
            _elevation_cache[cache_key] = 0.0
            return 0.0
            
    except requests.Timeout:
        logger.warning(f"Elevation lookup timed out for lat={lat}, lon={lon}. Using 0m as fallback.")
        _elevation_cache[f"{lat},{lon}"] = 0.0
        return 0.0
    except Exception as e:
        logger.warning(f"Elevation lookup failed: {str(e)}. Using 0m as fallback.")
        _elevation_cache[f"{lat},{lon}"] = 0.0
        return 0.0

def get_sun_moon_positions(dt: datetime, lat: float, lon: float) -> tuple[dict, dict]:
    """
    Calculate sun and moon positions for given datetime and location.
    Returns a tuple of dictionaries containing longitude and latitude for sun and moon.
    
    Note: For tithi calculations, we use geocentric positions as they are sufficient
    for determining the angular distance between Sun and Moon.
    """
    try:
        logger.debug(f"Calculating positions for dt={dt}, lat={lat}, lon={lon}")
        
        # Convert datetime to Julian day
        jd_et, jd_ut = datetime_to_jd(dt)
        logger.debug(f"Julian day: {jd_et}")
        
        # Set sidereal mode to Lahiri
        logger.debug("Set sidereal mode to Lahiri")
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        
        # Use global calculation flags with sidereal mode only
        flags = CALC_FLAGS | swe.FLG_SIDEREAL
        logger.debug(f"Calculation flags: {flags}")
        
        # Calculate sun position
        sun_result = swe.calc_ut(jd_ut, swe.SUN, flags)
        logger.debug(f"Sun calculation result: pos={sun_result}")
        
        # Calculate moon position
        moon_result = swe.calc_ut(jd_ut, swe.MOON, flags)
        logger.debug(f"Moon calculation result: pos={moon_result}")
        
        # Extract positions and create dictionaries
        sun_pos = {"longitude": sun_result[0][0], "latitude": sun_result[0][1]}
        moon_pos = {"longitude": moon_result[0][0], "latitude": moon_result[0][1]}
        
        logger.debug(f"Final positions - Sun: lon={sun_pos['longitude']}, lat={sun_pos['latitude']}")
        logger.debug(f"Final positions - Moon: lon={moon_pos['longitude']}, lat={moon_pos['latitude']}")
        
        return sun_pos, moon_pos
    except Exception as e:
        logger.error(f"Error calculating sun and moon positions: {str(e)}")
        raise ValueError(f"Failed to calculate sun and moon positions: {str(e)}")

def datetime_to_jd(dt: datetime) -> tuple[float, float]:
    """
    Convert datetime to Julian day numbers (both ET/TT and UT1).
    
    Args:
        dt: datetime object (timezone-aware recommended)
    
    Returns:
        tuple: (jd_et, jd_ut) where:
            - jd_et is the Julian day in Ephemeris Time (TT)
            - jd_ut is the Julian day in Universal Time (UT1)
    
    Raises:
        ValueError: If conversion fails
    """
    try:
        # Convert to UTC if not already
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        else:
            dt = dt.astimezone(pytz.UTC)
        
        logger.debug(f"Converting datetime {dt} to Julian day")
        logger.debug(f"Input datetime timezone: {dt.tzinfo}")
        logger.debug(f"UTC datetime: {dt}")
        
        # Extract components
        year = dt.year
        month = dt.month
        day = dt.day
        hour = dt.hour
        minute = dt.minute
        second = dt.second + dt.microsecond / 1000000.0
        
        logger.debug(f"Extracted components - Year: {year}, Month: {month}, Day: {day}")
        logger.debug(f"Extracted components - Hour: {hour}, Minute: {minute}, Second: {second}")
        
        # Convert to Julian day
        logger.debug("Calling swe.utc_to_jd with parameters:")
        logger.debug(f"  year={year}, month={month}, day={day}")
        logger.debug(f"  hour={hour}, minute={minute}, second={second}")
        logger.debug(f"  calendar=1")
        
        result = swe.utc_to_jd(year, month, day, hour, minute, second, 1)
        
        logger.debug(f"Raw result from swe.utc_to_jd: {result}")
        logger.debug(f"Result type: {type(result)}")
        logger.debug(f"Result length: {len(result)}")
        logger.debug(f"Result elements: {[type(x) for x in result]}")
        logger.debug(f"Result values: {result}")
        
        # Extract Julian day values
        jd_et, jd_ut = result
        
        logger.debug(f"Extracted JD values - ET: {jd_et}, UT: {jd_ut}")
        logger.debug(f"Final converted values - ET: {jd_et}, UT: {jd_ut}")
        
        return jd_et, jd_ut
    except Exception as e:
        logger.error(f"Error converting datetime to Julian day: {str(e)}")
        raise ValueError(f"Failed to convert datetime to Julian day: {str(e)}")

def jd_to_datetime(jd: float) -> datetime:
    """
    Convert Julian day (UT1) to UTC datetime object.
    
    Args:
        jd: Julian day number in UT1
    
    Returns:
        datetime: UTC datetime object
    """
    logger.debug(f"Converting JD {jd} to datetime")
    
    # Convert Julian day to UTC components using swe_jdut1_to_utc
    result = swe.jdut1_to_utc(jd, swe.GREG_CAL)
    
    # Extract components
    year = result[0]
    month = result[1]
    day = result[2]
    hour = result[3]
    minute = result[4]
    second = result[5]
    
    # Split second into second and microsecond
    second_int = int(second)
    microsecond = int((second - second_int) * 1000000)
    
    # Create datetime object
    dt = datetime(year, month, day, hour, minute, second_int, microsecond, tzinfo=pytz.UTC)
    logger.debug(f"Converted datetime: {dt}")
    return dt

def calculate_next_sunrise(dt: datetime, lat: float, lon: float, elevation: float = 0) -> datetime:
    """
    Calculate the next sunrise after the given datetime.
    
    Args:
        dt: datetime object (timezone-aware recommended)
        lat: latitude in degrees
        lon: longitude in degrees
        elevation: elevation in meters above sea level
    
    Returns:
        datetime: UTC datetime of next sunrise
    
    Raises:
        ValueError: If calculation fails or returns invalid results
    """
    logger.debug(f"Calculating next sunrise for dt={dt}, lat={lat}, lon={lon}, elev={elevation}")
    
    # Convert to UTC first
    utc_dt = dt.astimezone(pytz.UTC)
    logger.debug(f"UTC datetime: {utc_dt}")
    
    # Convert datetime to Julian day
    jd_et, jd_ut = datetime_to_jd(utc_dt)
    logger.debug(f"Julian day - ET: {jd_et}, UT: {jd_ut}")
    
    # Set sidereal mode to Lahiri
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    
    # Normalize coordinates slightly to avoid edge cases at the exact poles
    safe_lat = max(min(lat, 89.9999), -89.9999)
    safe_lon = max(min(lon, 180.0), -180.0)
    
    # rise_trans requires geopos as [lon, lat, elev]
    geopos = [safe_lon, safe_lat, elevation]
    logger.debug(f"Calculation parameters - geopos: {geopos}")
    
    try:
        # Calculate next sunrise using the correct parameter order
        result = swe.rise_trans(
            jd_ut,          # Julian day (UT)
            swe.SUN,        # Planet number
            swe.CALC_RISE,  # Rise/Set flag
            geopos,         # Geographic position [lon, lat, elev]
            0,              # Atmospheric pressure (use default)
            0,              # Temperature (use default)
            swe.FLG_SWIEPH  # Ephemeris flag
        )
        logger.debug(f"Sunrise calculation result: {result}")
    except Exception as e:
        logger.error(f\"Exception in swe.rise_trans for sunrise (lat={lat}, lon={lon}): {e}\")
        raise ValueError(f\"Failed to calculate sunrise with Swiss Ephemeris: {e}\")
    
    # rise_trans returns (return_code, (jd_rise, ...))
    if not isinstance(result, tuple) or len(result) != 2:
        raise ValueError(f"Invalid sunrise calculation result: {result}")
    
    # First element is the return code
    retcode = result[0]
    if retcode < 0:
        # -2: для этой даты/координат нет события восхода
        # (полярный день/ночь или циркумполярное Солнце)
        if retcode == -2:
            msg = (
                "No sunrise for this date and location "
                "(polar day/night or circumpolar Sun)"
            )
            exc = PolarDayNightError(msg)
        else:
            msg = f"Error calculating sunrise, Swiss Ephemeris code: {retcode}"
            exc = ValueError(msg)
        logger.warning(
            f"Swiss Ephemeris sunrise error {retcode} at lat={lat}, lon={lon}: {msg}"
        )
        raise exc
    
    # Second element is a tuple of 10 values, first one is the Julian day
    jd_rise = result[1][0]
    logger.debug(f\"Calculated sunrise JD: {jd_rise}\")
    
    # Convert Julian day to datetime
    rise_dt = jd_to_datetime(jd_rise)
    logger.debug(f\"Calculated sunrise time: {rise_dt}\")
    
    return rise_dt

def calculate_next_sunset(dt: datetime, lat: float, lon: float, elevation: float = 0) -> datetime:
    """
    Calculate the next sunset after the given datetime.
    
    Args:
        dt: datetime object (timezone-aware recommended)
        lat: latitude in degrees
        lon: longitude in degrees
        elevation: elevation in meters above sea level
    
    Returns:
        datetime: UTC datetime of next sunset
    
    Raises:
        ValueError: If calculation fails or returns invalid results
    """
    logger.debug(f"Calculating next sunset for dt={dt}, lat={lat}, lon={lon}, elev={elevation}")
    
    # Convert to UTC first
    utc_dt = dt.astimezone(pytz.UTC)
    logger.debug(f"UTC datetime: {utc_dt}")
    
    # Convert datetime to Julian day
    jd_et, jd_ut = datetime_to_jd(utc_dt)
    logger.debug(f"Julian day - ET: {jd_et}, UT: {jd_ut}")
    
    # Set sidereal mode to Lahiri
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    
    # Normalize coordinates slightly to avoid edge cases at the exact poles
    safe_lat = max(min(lat, 89.9999), -89.9999)
    safe_lon = max(min(lon, 180.0), -180.0)
    
    # rise_trans requires geopos as [lon, lat, elev]
    geopos = [safe_lon, safe_lat, elevation]
    logger.debug(f"Calculation parameters - geopos: {geopos}")
    
    try:
        # Calculate next sunset using the correct parameter order
        result = swe.rise_trans(
            jd_ut,          # Julian day (UT)
            swe.SUN,        # Planet number
            swe.CALC_SET,   # Rise/Set flag
            geopos,         # Geographic position [lon, lat, elev]
            0,              # Atmospheric pressure (use default)
            0,              # Temperature (use default)
            swe.FLG_SWIEPH  # Ephemeris flag
        )
        logger.debug(f"Sunset calculation result: {result}")
    except Exception as e:
        logger.error(f"Exception in swe.rise_trans for sunset (lat={lat}, lon={lon}): {e}")
        raise ValueError(f"Failed to calculate sunset with Swiss Ephemeris: {e}")
    
    # rise_trans returns (return_code, (jd_set, ...))
    if not isinstance(result, tuple) or len(result) != 2:
        raise ValueError(f"Invalid sunset calculation result: {result}")
    
    # First element is the return code
    retcode = result[0]
    if retcode < 0:
        if retcode == -2:
            msg = (
                "No sunset for this date and location "
                "(polar day/night or circumpolar Sun)"
            )
            exc = PolarDayNightError(msg)
        else:
            msg = f"Error calculating sunset, Swiss Ephemeris code: {retcode}"
            exc = ValueError(msg)
        logger.warning(
            f"Swiss Ephemeris sunset error {retcode} at lat={lat}, lon={lon}: {msg}"
        )
        raise exc
    
    # Second element is a tuple of 10 values, first one is the Julian day
    jd_set = result[1][0]
    logger.debug(f"Calculated sunset JD: {jd_set}")
    
    # Convert Julian day to datetime
    set_dt = jd_to_datetime(jd_set)
    logger.debug(f"Calculated sunset time: {set_dt}")
    
    return set_dt

def get_sun_longitude(jd: float) -> float:
    """
    Get the sun's longitude at the given Julian day using Vedic system.
    Uses Ephemeris Time (ET/TT) for accurate astronomical calculations.
    
    Args:
        jd: Julian day number (ET/TT)
    
    Returns:
        float: Sun's longitude in degrees
    
    Raises:
        ValueError: If calculation fails
    """
    logger.debug(f"Calculating sun longitude for JD (ET) {jd}")
    
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    
    result = swe.calc(jd, swe.SUN, flags)  # Use calc() for ET instead of calc_ut()
    debug_swe_calc("Sun longitude", jd, result)
    
    if result[0] < 0:
        raise ValueError(f"Error calculating Sun longitude: {result}")
    
    longitude = float(result[1][0])
    logger.debug(f"Sun longitude: {longitude}")
    return longitude

def get_moon_longitude(jd: float) -> float:
    """
    Get the moon's longitude at the given Julian day using Vedic system.
    Uses Ephemeris Time (ET/TT) for accurate astronomical calculations.
    
    Args:
        jd: Julian day number (ET/TT)
    
    Returns:
        float: Moon's longitude in degrees
    
    Raises:
        ValueError: If calculation fails
    """
    logger.debug(f"Calculating moon longitude for JD (ET) {jd}")
    
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    
    result = swe.calc(jd, swe.MOON, flags)  # Use calc() for ET instead of calc_ut()
    debug_swe_calc("Moon longitude", jd, result)
    
    if result[0] < 0:
        raise ValueError(f"Error calculating Moon longitude: {result}")
    
    longitude = float(result[1][0])
    logger.debug(f"Moon longitude: {longitude}")
    return longitude

def get_sunrise_sunset_times(dt: datetime, lat: float, lon: float) -> tuple[datetime, datetime]:
    """
    Calculate sunrise and sunset times for the given date and location.
    Uses an improved algorithm that handles equatorial locations better.
    
    Args:
        dt: datetime object (timezone-aware recommended)
        lat: latitude in degrees
        lon: longitude in degrees
    
    Returns:
        tuple: (sunrise_dt, sunset_dt) where both are UTC datetime objects
    
    Raises:
        ValueError: If calculation fails
    """
    logger.debug(f"Calculating sunrise and sunset times for dt={dt}, lat={lat}, lon={lon}")
    
    # Get elevation
    elev = get_elevation(lat, lon)
    
    # Start from the beginning of the current day
    start_dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    prev_dt = start_dt - timedelta(days=1)
    
    # Calculate sunrise and sunset for previous and current day
    prev_sunrise = calculate_next_sunrise(prev_dt, lat, lon, elev)
    prev_sunset = calculate_next_sunset(prev_dt, lat, lon, elev)
    curr_sunrise = calculate_next_sunrise(prev_sunset, lat, lon, elev)
    curr_sunset = calculate_next_sunset(curr_sunrise, lat, lon, elev)
    
    # Normalize times to ensure they're in the correct order
    if curr_sunrise.date() == dt.date() and curr_sunset.date() == dt.date():
        # Both times are on the requested date
        if curr_sunrise < curr_sunset:
            sunrise, sunset = curr_sunrise, curr_sunset
        else:
            sunrise, sunset = prev_sunrise, curr_sunset
    elif curr_sunrise.date() == dt.date():
        # Only sunrise is on the requested date
        sunrise, sunset = curr_sunrise, prev_sunset
    elif curr_sunset.date() == dt.date():
        # Only sunset is on the requested date
        sunrise, sunset = prev_sunrise, curr_sunset
    else:
        # Neither time is on the requested date, use the next available pair
        sunrise, sunset = curr_sunrise, curr_sunset
    
    logger.debug(f\"Final sunrise time: {sunrise}\")
    logger.debug(f\"Final sunset time: {sunset}\")
    
    return sunrise, sunset 

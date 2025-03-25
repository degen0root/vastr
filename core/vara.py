from datetime import datetime, timezone
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Detailed Vara information in English
VARA_INFO = {
    "Soma": {
        "name": "Monday",
        "favorable": "Favorable",
        "ruler": "Moon"
    },
    "Mangala": {
        "name": "Tuesday",
        "favorable": "Unfavorable",
        "ruler": "Mars"
    },
    "Budha": {
        "name": "Wednesday",
        "favorable": "Favorable",
        "ruler": "Mercury"
    },
    "Guru": {
        "name": "Thursday",
        "favorable": "Favorable",
        "ruler": "Jupiter"
    },
    "Shukra": {
        "name": "Friday",
        "favorable": "Favorable",
        "ruler": "Venus"
    },
    "Shani": {
        "name": "Saturday",
        "favorable": "Unfavorable",
        "ruler": "Saturn"
    },
    "Ravi": {
        "name": "Sunday",
        "favorable": "Favorable",
        "ruler": "Sun"
    }
}

def calculate_vara(datetime_obj: datetime) -> Dict[str, str]:
    """
    Calculate the Vara (weekday) and its detailed information for a given datetime.
    
    Args:
        datetime_obj (datetime): The datetime to calculate Vara for
        
    Returns:
        Dict[str, str]: Dictionary containing Vara information in English
    """
    try:
        # Get weekday (0 = Monday, 6 = Sunday)
        weekday = datetime_obj.weekday()
        
        # Map weekday numbers to Vara names
        vara_mapping = {
            0: "Soma",     # Monday (Moon's Day)
            1: "Mangala",  # Tuesday (Mars's Day)
            2: "Budha",    # Wednesday (Mercury's Day)
            3: "Guru",     # Thursday (Jupiter's Day)
            4: "Shukra",   # Friday (Venus's Day)
            5: "Shani",    # Saturday (Saturn's Day)
            6: "Ravi"      # Sunday (Sun's Day)
        }
        
        vara = vara_mapping[weekday]
        vara_info = VARA_INFO[vara]
        
        result = {
            "vara": vara,
            "name": vara_info["name"],
            "favorable": vara_info["favorable"],
            "ruler": vara_info["ruler"]
        }
        
        logger.debug(f"Calculated Vara info: {result} for datetime: {datetime_obj}")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating Vara: {str(e)}")
        return {
            "vara": "Unknown",
            "name": "Unknown",
            "favorable": "Unknown",
            "ruler": "Unknown"
        } 
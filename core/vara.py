from datetime import datetime
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Detailed Vara information in Russian
VARA_INFO = {
    "Soma": {
        "name": "Понедельник",
        "favorable": "Благоприятный",
        "ruler": "Луна"
    },
    "Mangala": {
        "name": "Вторник",
        "favorable": "Неблагоприятный",
        "ruler": "Марс"
    },
    "Budha": {
        "name": "Среда",
        "favorable": "Благоприятный",
        "ruler": "Меркурий"
    },
    "Guru": {
        "name": "Четверг",
        "favorable": "Благоприятный",
        "ruler": "Юпитер"
    },
    "Shukra": {
        "name": "Пятница",
        "favorable": "Благоприятный",
        "ruler": "Венера"
    },
    "Shani": {
        "name": "Суббота",
        "favorable": "Неблагоприятный",
        "ruler": "Сатурн"
    },
    "Ravi": {
        "name": "Воскресенье",
        "favorable": "Благоприятный",
        "ruler": "Солнце"
    }
}

def calculate_vara(datetime_obj: datetime) -> Dict[str, str]:
    """
    Calculate the Vara (weekday) and its detailed information for a given datetime.
    
    Args:
        datetime_obj (datetime): The datetime to calculate Vara for
        
    Returns:
        Dict[str, str]: Dictionary containing Vara information in Russian
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
            "name": "Неизвестно",
            "favorable": "Неизвестно",
            "ruler": "Неизвестно"
        } 
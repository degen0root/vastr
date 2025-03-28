from typing import Dict, Any, List
from pydantic import BaseModel, field_validator

class SunPosition(BaseModel):
    longitude: float
    latitude: float
    status: str = "Favorable"  # Sun is generally favorable

class MoonPosition(BaseModel):
    longitude: float
    latitude: float
    status: str = "Favorable"  # Moon is generally favorable

class Times(BaseModel):
    sunrise: str
    sunset: str
    status: str = "Favorable"  # Sunrise and sunset are generally favorable times

class VaraInfo(BaseModel):
    vara: str
    name: str
    status: str  # Favorable, Unfavorable, or Neutral
    ruler: str

class TithiInfo(BaseModel):
    number: int
    name: str
    status: str  # Favorable, Unfavorable, or Neutral
    start: str
    end: str

class Nakshatra(BaseModel):
    number: int
    name: str
    status: str  # Favorable, Unfavorable, or Neutral
    start: str
    end: str
    constellation: str  # Current moon constellation

class CelestialPosition(BaseModel):
    longitude: float
    latitude: float

class RawData(BaseModel):
    sun: CelestialPosition
    moon: CelestialPosition

class Yoga(BaseModel):
    number: int
    name: str
    status: str  # Favorable, Unfavorable, or Neutral
    start: str
    end: str

class Karana(BaseModel):
    number: int
    name: str
    status: str  # Favorable or Unfavorable
    start: str
    end: str

class PanchangaResponse(BaseModel):
    sun: SunPosition
    moon: MoonPosition
    times: Dict[str, str]
    vara: VaraInfo
    tithi: TithiInfo
    nakshatra: Nakshatra
    yoga: Yoga
    karana: Karana


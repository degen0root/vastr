from typing import Dict, Any, List
from pydantic import BaseModel, field_validator

class SunPosition(BaseModel):
    longitude: float
    latitude: float

class MoonPosition(BaseModel):
    longitude: float
    latitude: float

class Times(BaseModel):
    sunrise: str
    sunset: str

class VaraInfo(BaseModel):
    vara: str
    name: str
    favorable: str
    ruler: str

class TithiInfo(BaseModel):
    number: int
    name: str
    favorable: str
    start: str
    end: str

class Nakshatra(BaseModel):
    number: int
    name: str
    favorable: str
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
    favorable: str
    start: str
    end: str

class Karana(BaseModel):
    number: int
    name: str
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


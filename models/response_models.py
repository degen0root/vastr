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
    start: str
    end: str

class Nakshatra(BaseModel):
    number: int
    name: str
    start: str
    end: str

class KaranaInfo(BaseModel):
    number: int
    name: str
    activity: str
    start: str
    end: str
    ruler: str
    deity: str
    favorable_activities: List[str]
    is_auspicious: bool

class YogaInfo(BaseModel):
    number: int
    name: str
    description: str
    ruler: str
    deity: str
    start: str
    end: str
    is_auspicious: bool

class CelestialPosition(BaseModel):
    longitude: float
    latitude: float

class RawData(BaseModel):
    sun: CelestialPosition
    moon: CelestialPosition

class Yoga(BaseModel):
    number: int
    name: str
    start: str
    end: str

class PanchangaResponse(BaseModel):
    sun: SunPosition
    moon: MoonPosition
    times: Times
    vara: VaraInfo
    tithi: TithiInfo
    nakshatra: Nakshatra
    yoga: Yoga 
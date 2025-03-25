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

class NakshatraInfo(BaseModel):
    number: int
    name: str
    ruler: str
    deity: str
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

class PanchangaResponse(BaseModel):
    sun: Dict[str, float]
    moon: Dict[str, float]
    times: Dict[str, str]
    vara: VaraInfo
    tithi: TithiInfo
    nakshatra: NakshatraInfo 
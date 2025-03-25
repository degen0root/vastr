import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pytz
import swisseph as swe
import logging
from pydantic import BaseModel
from typing import Optional

from models.request_models import PanchangaRequest
from models.response_models import PanchangaResponse, SunPosition, MoonPosition, Times, VaraInfo, TithiInfo
from utils.astronomy import get_sun_moon_positions, get_sunrise_sunset_times
from core.vara import calculate_vara
from core.tithi import calculate_tithi
from core.nakshatra import calculate_nakshatra
from core.yoga import calculate_yoga

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Swiss Ephemeris
ephe_path = os.path.join(os.path.dirname(__file__), "ephe")
logger.debug(f"Setting ephemeris path to: {ephe_path}")
logger.debug(f"Ephemeris directory exists: {os.path.exists(ephe_path)}")
logger.debug(f"Ephemeris directory contents: {os.listdir(ephe_path)}")
swe.set_ephe_path(ephe_path)

# Set Ayanamsa to Lahiri (Indian)
swe.set_sid_mode(swe.SIDM_LAHIRI)

# Create FastAPI app
app = FastAPI(
    title="Vastr Panchanga API",
    description="API for calculating Vedic astrological elements (Panchanga)",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PanchangaRequest(BaseModel):
    datetime: str
    latitude: float
    longitude: float

@app.post("/panchanga", response_model=PanchangaResponse)
async def calculate_panchanga(request: PanchangaRequest):
    """
    Calculate Panchanga elements for a given datetime and location.
    """
    try:
        # Convert datetime to UTC
        dt = datetime.fromisoformat(request.datetime.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        
        # Calculate positions
        sun_pos, moon_pos = get_sun_moon_positions(dt, request.latitude, request.longitude)
        sunrise, sunset = get_sunrise_sunset_times(dt, request.latitude, request.longitude)
        
        # Calculate Vara
        vara = calculate_vara(dt)
        
        # Calculate Tithi
        tithi = calculate_tithi(dt, request.latitude, request.longitude)
        
        # Calculate Nakshatra
        nakshatra = calculate_nakshatra(dt, request.latitude, request.longitude)
        
        # Calculate Yoga
        yoga = calculate_yoga(dt, request.latitude, request.longitude)
        
        return PanchangaResponse(
            sun=sun_pos,
            moon=moon_pos,
            times={"sunrise": sunrise.isoformat(), "sunset": sunset.isoformat()},
            vara=vara,
            tithi=tithi,
            nakshatra=nakshatra,
            yoga=yoga
        )
        
    except Exception as e:
        logger.error(f"Error calculating Panchanga: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
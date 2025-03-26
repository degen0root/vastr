# Vastr Panchanga API

A FastAPI-based service that calculates various elements of the Hindu Panchānga (Vedic calendar) based on astronomical positions. The service provides accurate calculations for:

- Tithi (lunar day)
- Nakshatra (lunar mansion)
- Yoga (lunar-solar combination)
- Karana (half of tithi)
- Vara (weekday)
- Sunrise and sunset times

## Features

- **Astronomical Precision**: Uses Swiss Ephemeris for accurate planetary positions
- **Geographic Support**: Calculates positions for any location on Earth
- **Comprehensive Panchānga**: Includes all five main elements of the Hindu calendar
- **RESTful API**: Simple HTTP interface for easy integration
- **Docker Support**: Easy deployment with containerization

## API Endpoints

### POST /panchanga

Calculate all Panchānga elements for a given date, time, and location.

**Request Model:**
```python
class PanchangaRequest(BaseModel):
    datetime: datetime  # UTC datetime
    latitude: float    # Latitude in degrees (-90 to 90)
    longitude: float   # Longitude in degrees (-180 to 180)
```

**Request Body:**
```json
{
    "datetime": "2025-03-28T14:00:00Z",
    "latitude": 51.4769,
    "longitude": -0.0005
}
```

**Response:**
```json
{
    "sun": {
        "longitude": 343.92766334165924,
        "latitude": -5.49816023014652e-05
    },
    "moon": {
        "longitude": 331.6786008209587,
        "latitude": -0.14239403000977088
    },
    "times": {
        "sunrise": "2025-03-28T05:43:49.830488+00:00",
        "sunset": "2025-03-28T18:27:07.902375+00:00"
    },
    "vara": {
        "vara": "Shukra",
        "name": "Friday",
        "favorable": "Favorable",
        "ruler": "Venus"
    },
    "tithi": {
        "number": 29,
        "start": "2025-03-27T17:33:54.958921+00:00",
        "end": "2025-03-28T14:25:44.926334+00:00"
    },
    "nakshatra": {
        "number": 25,
        "name": "Purva Bhadrapada",
        "start": "2025-03-27T19:03:46.478219+00:00",
        "end": "2025-03-28T16:39:35.983116+00:00"
    },
    "yoga": {
        "number": 24,
        "name": "Shukla",
        "start": "2025-03-28T00:26:33.478341+00:00",
        "end": "2025-03-28T20:36:56.558741+00:00"
    },
    "karana": {
        "number": 8,
        "name": "Shakuni",
        "start": "2025-03-28T04:02:53.097498+00:00",
        "end": "2025-03-28T14:25:44.926334+00:00"
    }
}
```

## Panchānga Elements

### Tithi (Lunar Day)
- Represents the angular distance (12°) between the Sun and Moon
- 30 tithis in a lunar month (15 in Shukla Paksha, 15 in Krishna Paksha)
- Each tithi is divided into two karanas
- **Calculation Method**:
  - Calculate the difference between Moon and Sun longitudes
  - Each tithi spans 12° of this difference
  - Tithi number = (moon_sun_diff / 12) + 1
  - Start/end times found by binary search for exact 12° boundaries
  - Shukla Paksha: Tithis 1-15 (waxing moon)
  - Krishna Paksha: Tithis 16-30 (waning moon)

### Karana (Half of Tithi)
- Represents 6° of the Moon's movement from the Sun
- 11 karanas in total:
  - 7 movable (Chara): Bava, Balava, Kaulava, Taitila, Gara, Vanija, Vishti
  - 4 fixed (Sthira): Shakuni, Chatushpada, Naga, Kimstughna
- Fixed karanas appear on specific tithis:
  - Shakuni: Chaturdashi in Krishna Paksha
  - Chatushpada & Naga: Amavasya
  - Kimstughna: Purnima
- **Calculation Method**:
  - Each tithi contains exactly 2 karanas (6° each)
  - Movable karanas follow a cycle of 7 (repeating every 8 tithis)
  - Fixed karanas appear on specific tithis based on traditional rules
  - Boundaries calculated astronomically using binary search for 6° crossings
  - Vishti (Bhadra) karana is considered inauspicious for important activities

### Nakshatra (Lunar Mansion)
- Represents the Moon's position relative to fixed stars
- 27 nakshatras in total
- Each nakshatra spans 13°20' of the ecliptic
- **Calculation Method**:
  - Calculate Moon's longitude relative to fixed stars
  - Each nakshatra spans 13°20' (13.333... degrees)
  - Nakshatra number = (moon_longitude / 13.333...) + 1
  - Start/end times found by binary search for exact 13°20' boundaries
  - Each nakshatra has a ruling planet and deity
  - Used for determining auspicious times and personal characteristics

### Yoga (Lunar-Solar Combination)
- Represents the sum of Sun and Moon longitudes
- 27 yogas in total
- Each yoga spans 13°20' of the ecliptic
- **Calculation Method**:
  - Add Sun and Moon longitudes (modulo 360°)
  - Each yoga spans 13°20' (13.333... degrees)
  - Yoga number = (combined_longitude / 13.333...) + 1
  - Start/end times found by binary search for exact 13°20' boundaries
  - Yogas influence the overall nature of the day
  - Some yogas are considered auspicious, others inauspicious

### Vara (Weekday)
- Traditional weekday with additional attributes
- Includes favorable/inauspicious status and planetary ruler
- **Calculation Method**:
  - Determine weekday from Julian Day Number
  - Each day has a ruling planet:
    - Sunday (Ravi): Sun
    - Monday (Soma): Moon
    - Tuesday (Mangala): Mars
    - Wednesday (Budha): Mercury
    - Thursday (Guru): Jupiter
    - Friday (Shukra): Venus
    - Saturday (Shani): Saturn
  - Favorable status based on traditional rules:
    - Monday, Wednesday, Thursday, Friday: Generally favorable
    - Tuesday, Saturday: Generally unfavorable
    - Sunday: Neutral
  - Used for determining auspicious days for various activities

### Astronomical Calculations
All calculations are based on precise astronomical positions using the Swiss Ephemeris:
- Sun and Moon positions calculated for exact requested time
- Longitudes and latitudes in ecliptic coordinates
- All times in UTC with proper timezone handling
- Binary search used to find exact boundary times
- Sunrise and sunset times calculated for given location

## Installation

1. Clone the repository:
```bash
git clone https://github.com/akaalius/vastr.git
cd vastr
```

2. Build and run with Docker:
```bash
docker build -t vastr-panchanga-api .
docker run -d -p 8000:8000 vastr-panchanga-api
```

3. Or run locally:
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the service is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

The project structure:
```
vastr/
├── core/
│   ├── tithi.py      # Tithi calculations
│   ├── nakshatra.py  # Nakshatra calculations
│   ├── yoga.py       # Yoga calculations
│   ├── karana.py     # Karana calculations
│   └── vara.py       # Vara calculations
├── utils/
│   └── astronomy.py  # Astronomical calculations
├── models/
│   ├── request_models.py   # Request Pydantic models
│   └── response_models.py  # Response Pydantic models
├── main.py           # FastAPI application
├── requirements.txt  # Python dependencies
└── Dockerfile       # Container configuration
```

### Data Models

#### Request Models
- `PanchangaRequest`: Input model for the /panchanga endpoint
  - `datetime`: UTC datetime for calculations
  - `latitude`: Geographic latitude (-90° to 90°)
  - `longitude`: Geographic longitude (-180° to 180°)

#### Response Models
- `SunPosition`: Sun's astronomical position
  - `longitude`: Ecliptic longitude
  - `latitude`: Ecliptic latitude
- `MoonPosition`: Moon's astronomical position
  - `longitude`: Ecliptic longitude
  - `latitude`: Ecliptic latitude
- `Times`: Sunrise and sunset times
- `Vara`: Weekday information
- `Tithi`: Lunar day information
- `Nakshatra`: Lunar mansion information
- `Yoga`: Lunar-solar combination information
- `Karana`: Half-tithi information

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
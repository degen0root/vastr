# Vastr - Vedic Astrological System for Time Reckoning

A modern FastAPI-based service for calculating Vedic astrological elements (Panchanga) using the Swiss Ephemeris library.

## Features

- Calculates all five elements of Panchanga:
  1. Vara (Weekday)
  2. Tithi (Lunar Day)
  3. Nakshatra (Lunar Mansion)
  4. Karana (Half-Tithi)
  5. Yoga (Sun-Moon Combination)
- Uses high-precision Swiss Ephemeris calculations
- Supports timezone detection based on coordinates
- Provides detailed information about each astrological element
- RESTful API with JSON responses
- CORS-enabled for web applications
- Containerized with Docker for easy deployment

## Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/vastr.git
cd vastr
```

2. Build and start the container:
```bash
docker compose up -d
```

The API will be available at `http://localhost:8000`

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/vastr.git
cd vastr
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the server:
```bash
python main.py
```

## Docker Commands

### Building the Container
```bash
docker compose build
```

### Starting the Container
```bash
docker compose up -d
```

### Stopping the Container
```bash
docker compose down
```

### Viewing Logs
```bash
docker compose logs -f
```

### Rebuilding and Restarting
```bash
docker compose down && docker compose up -d --build
```

## API Usage

### Example Request
```bash
curl -X POST "http://localhost:8000/panchanga" \
     -H "Content-Type: application/json" \
     -d '{
       "datetime": "2024-03-22 08:00",
       "latitude": 12.9716,
       "longitude": 77.5946,
       "elevation": 920
     }'
```

## API Documentation

### POST /panchanga

Calculate Panchanga elements for a given datetime and location.

#### Request Body

```json
{
  "datetime": "YYYY-MM-DD HH:MM",
  "latitude": float,
  "longitude": float,
  "elevation": float (optional),
  "timezone": string (optional)
}
```

#### Response

```json
{
  "vara": {
    "number": int,
    "name": string,
    "is_auspicious": boolean,
    "sunrise": string,
    "sunset": string,
    "next_sunrise": string,
    "ruler": string,
    "deities": string[],
    "resonant_nakshatras": string[]
  },
  "tithi": {
    "number": int,
    "name": string,
    "element": string,
    "activity": string,
    "start": string,
    "end": string,
    "paksha": string,
    "ruler": string,
    "deity": string,
    "type": string
  },
  "nakshatra": {
    "number": int,
    "name": string,
    "ruler": string,
    "type": string,
    "start": string,
    "end": string,
    "is_auspicious": boolean
  },
  "karana": {
    "number": int,
    "name": string,
    "activity": string,
    "start": string,
    "end": string,
    "ruler": string,
    "deity": string,
    "favorable_activities": string[],
    "is_auspicious": boolean
  },
  "yoga": {
    "number": int,
    "name": string,
    "description": string,
    "start": string,
    "end": string,
    "ruler": string,
    "deity": string,
    "is_auspicious": boolean
  }
}
```

## Project Structure

```
vastr/
├── core/
│   ├── vara.py
│   ├── tithi.py
│   ├── nakshatra.py
│   ├── karana.py
│   └── yoga.py
├── models/
│   ├── request_models.py
│   └── response_models.py
├── utils/
│   └── astronomy.py
├── ephe/
│   └── ... (ephemeris files)
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
└── README.md
```

## Dependencies

- FastAPI: Modern web framework for building APIs
- Uvicorn: ASGI server for running FastAPI
- Swiss Ephemeris: High-precision astronomical calculations
- TimezoneFinder: Determine timezone from coordinates
- PyTZ: Timezone database and utilities
- Pydantic: Data validation using Python type annotations

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Swiss Ephemeris for providing high-precision astronomical calculations
- FastAPI for the excellent web framework
- The Vedic astrology community for preserving this knowledge 
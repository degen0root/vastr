# Vastr Panchanga API

A RESTful API service that calculates Vedic Panchanga (astrological calendar) elements including Vara (weekday), Tithi (lunar day), Nakshatra (lunar mansion), and Yoga (lunar-solar combination) for any given date, time, and location.

## Features

- **Vara (Weekday) Calculation**
  - Calculates the weekday and its astrological properties
  - Includes favorable/unfavorable status and planetary ruler
  - Supports all seven weekdays with their Sanskrit names (Ravi, Soma, Mangala, Budha, Guru, Shukra, Shani)

- **Tithi (Lunar Day) Calculation**
  - Determines the current tithi (lunar day)
  - Provides start and end times of the tithi
  - Calculates absolute tithi number (1-30)

- **Nakshatra (Lunar Mansion) Calculation**
  - Identifies the current nakshatra (lunar mansion)
  - Provides start and end times of the nakshatra
  - Includes nakshatra number (1-27) and name
  - Calculates planetary ruler for each nakshatra

- **Yoga (Lunar-Solar Combination) Calculation**
  - Calculates the current yoga based on combined positions of Sun and Moon
  - Provides start and end times of the yoga
  - Includes yoga number (1-27) and name
  - Each yoga spans 13.333... degrees of combined Sun-Moon longitude

## Installation

### Prerequisites

- Python 3.11 or higher
- Docker (optional, for containerized deployment)

### Local Installation

1. Clone the repository:
```bash
git clone https://github.com/akaalius/vastr.git
cd vastr
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the API:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker Installation

1. Build and run the container:
```bash
docker stop vastr-panchanga-api; docker rm vastr-panchanga-api; docker build -t vastr-panchanga-api . && docker run -d --name vastr-panchanga-api -p 8000:8000 vastr-panchanga-api
```

This command will:
- Stop any existing container named `vastr-panchanga-api`
- Remove the old container
- Build a new Docker image from the current directory
- Run a new container in detached mode (-d)
- Name the container `vastr-panchanga-api`
- Map port 8000 from the container to the host

The API will be available at `http://localhost:8000`

## Usage

### API Endpoints

#### POST /panchanga

Calculate all Panchanga elements for a given datetime and location.

**Request:**
```json
{
    "datetime": "2025-04-04T14:00:00Z",
    "latitude": 51.4769,
    "longitude": -0.0005
}
```

**Response:**
```json
{
    "sun": {
        "longitude": 350.8387606169285,
        "latitude": 0.00010088933104459311
    },
    "moon": {
        "longitude": 74.46095747888872,
        "latitude": 5.166799261185946
    },
    "times": {
        "sunrise": "2025-04-04T05:27:59.554894+00:00",
        "sunset": "2025-04-04T18:38:51.842954+00:00"
    },
    "vara": {
        "vara": "Shukra",
        "name": "Friday",
        "favorable": "Favorable",
        "ruler": "Venus"
    },
    "tithi": {
        "number": 7,
        "start": "2025-04-03T16:11:52.704630+00:00",
        "end": "2025-04-04T14:43:10.959566+00:00"
    },
    "nakshatra": {
        "number": 6,
        "name": "Ardra",
        "start": "2025-04-04T00:21:14.675765+00:00",
        "end": "2025-04-04T23:50:34.979206+00:00"
    },
    "yoga": {
        "number": 5,
        "name": "Shobhana",
        "start": "2025-04-03T18:31:19.207549+00:00",
        "end": "2025-04-04T16:15:14.020255+00:00"
    }
}
```

### Example Usage with curl

```bash
curl -X POST "http://localhost:8000/panchanga" \
     -H "Content-Type: application/json" \
     -d '{
           "datetime": "2025-04-04T14:00:00Z",
           "latitude": 51.4769,
           "longitude": -0.0005
         }'
```

### Example Usage with Python

```python
import requests

url = "http://localhost:8000/panchanga"
data = {
    "datetime": "2025-04-04T14:00:00Z",
    "latitude": 51.4769,
    "longitude": -0.0005
}

response = requests.post(url, json=data)
print(response.json())
```

## Development

### Project Structure

```
vastr/
├── core/
│   ├── vara.py      # Weekday calculations
│   ├── tithi.py     # Lunar day calculations
│   ├── nakshatra.py # Lunar mansion calculations
│   └── yoga.py      # Lunar-solar combination calculations
├── utils/
│   └── astronomy.py # Astronomical calculations
├── main.py          # FastAPI application
├── requirements.txt # Python dependencies
└── Dockerfile      # Container configuration
```

### Running Tests

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
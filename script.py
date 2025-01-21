from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, Union, List
import httpx
import asyncio
import json
import uvicorn
from datetime import datetime
from contextlib import asynccontextmanager


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
DATA_FILE = "database.json"


# Models
class City(BaseModel):
    latitude: float
    longitude: float
    weather: Optional[Dict] = None
    last_updated: Optional[str] = None


class User(BaseModel):
    username: str
    tracked_cities: Dict[str, City] = {}


def load_database() -> Dict[int, User]:
    try:
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
            return {int(user_id): User(**user) for user_id, user in data.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_database(users_data: Dict[int, User]):
    with open(DATA_FILE, "w") as file:
        json.dump({str(user_id): user.dict()
                  for user_id, user in users_data.items()}, file, indent=4)


# global var
users_data = load_database()


@asynccontextmanager
async def lifespan(app: FastAPI):
    weather_task = asyncio.create_task(scheduled_weather_updates())
    yield
    weather_task.cancel()

app = FastAPI(lifespan=lifespan)


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "API launched"}


@app.get("/weather")
async def get_weather(lat: float, lon: float) -> Dict[str, Optional[float]]:
    params = {"latitude": lat,
              "longitude": lon,
              "current_weather": True,
              "hourly": "pressure_msl",
              "timezone": "Europe/Moscow"
              }

    async with httpx.AsyncClient() as client:
        response = await client.get(OPEN_METEO_URL, params=params)
        response.raise_for_status()
        data = response.json()
        current_weather = data.get("current_weather", {})
        hourly_data = data.get("hourly", {})
        pressure = hourly_data.get("pressure_msl", [None])[0]
        return {
            "temperature": current_weather.get("temperature"),
            "wind_speed": current_weather.get("windspeed"),
            "pressure": pressure,
        }


@app.post("/register_user")
def register_user(username: str) -> Dict[str, Union[int, str]]:
    if username in [user.username for user in users_data.values()]:
        raise HTTPException(status_code=400, detail="Username already exists")

    user_id = len(users_data) + 1
    users_data[user_id] = User(username=username)
    save_database(users_data)
    return {"user_id": user_id, "username": username}


@app.post("/track_city")
async def track_city(user_id: int, city: str, lat: float, lon: float) -> Dict[str, str]:
    if user_id not in users_data:
        raise HTTPException(status_code=404, detail="User not found")

    users_data[user_id].tracked_cities[city] = City(
        latitude=lat, longitude=lon)
    save_database(users_data)
    await update_weather_for_city(user_id, city)
    return {"message": f"Start weather tracking for {city}"}


@app.get("/tracked_cities")
def get_tracked_cities(user_id: int) -> List[str]:
    if user_id not in users_data:
        raise HTTPException(status_code=404, detail="User not found")
    return list(users_data[user_id].tracked_cities.keys())


@app.get("/city_weather")
async def city_weather(user_id: int, city: str, time: str, parameters: str = "temperature_2m,windspeed_10m,relative_humidity_2m,precipitation") -> Dict[str, Union[float, str]]:
    if user_id not in users_data:
        raise HTTPException(status_code=404, detail="User not found")
    if city not in users_data[user_id].tracked_cities:
        raise HTTPException(status_code=404, detail="City not being tracked")

    city_data = users_data[user_id].tracked_cities[city]
    params = {
        "latitude": city_data.latitude,
        "longitude": city_data.longitude,
        "hourly": parameters,
        "timezone": "Europe/Moscow"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(OPEN_METEO_URL, params=params)
        response.raise_for_status()
        data = response.json()
        hourly_data = data.get("hourly", {})
        time_index = data["hourly"]["time"].index(time)

        result = {}
        for param in parameters.split(','):
            if param in hourly_data:
                result[param] = hourly_data[param][time_index]

        return result


@app.get("/database")
def get_database() -> Dict[int, User]:
    return users_data


@app.post("/reset_database")
def reset_database() -> Dict[str, str]:
    global users_data
    users_data = {}
    save_database(users_data)
    return {"message": "Database has been reset"}


async def update_weather_for_city(user_id: str, city: str, timezone: str = "Europe/Moscow"):
    city = users_data[user_id].tracked_cities[city]

    params = {
        "latitude": city.latitude,
        "longitude": city.longitude,
        "current_weather": True,
        "timezone": timezone
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(OPEN_METEO_URL, params=params)
        response.raise_for_status()
        city.weather = response.json().get("current_weather", {})
        city.last_updated = datetime.now().isoformat()
        save_database(users_data)


async def scheduled_weather_updates():
    while True:
        for user_id in users_data:
            for city in users_data[user_id].tracked_cities:
                await update_weather_for_city(user_id, city, timezone="Europe/Moscow")
        await asyncio.sleep(900)


if __name__ == "__main__":
    uvicorn.run("script:app", host="127.0.0.1", port=8000, reload=True)

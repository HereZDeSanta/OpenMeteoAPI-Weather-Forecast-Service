
# Описание API методов

## 1. Главная страница:
**GET /** - возвращает сообщение о запуске API.

**Пример запроса:**
`curl "http://127.0.0.1:8000/"`


**Пример ответа:**
```
{
  "message": "API launched"
}
```

## 2. Получение текущей погоды (по координатам):
**GET /weather** - Получение текущей погоды, согласно указанной географической точке (широта, долгота).


**Параметры:**
- `lat` (float): Широта;
- `lon` (float): Долгота.

**Пример запроса:**

`curl "http://127.0.0.1:8000/weather?lat=59.9386&lon=30.3141"`

**Пример ответа:**

```
{
  "temperature": 2.6,
  "wind_speed": 21.6,
  "pressure": 1011.3
}
```

## 3. Регистрация пользователя:
**POST /register_user** - Регистрирует нового пользователя и возвращает его id.

**Параметры:**
- `username` (str): Имя пользователя.

**Пример запроса:**

`curl -X 'POST' "http://127.0.0.1:8000/register_user?username=Danila"`

**Пример ответа:**

```
{
  "user_id": 1,
  "username": "Danila"
}
```

## 4. Добавление города для отслеживания:
**POST /track_city** - Добавляет город для отслеживания погоды для указанного пользоватея (по id).

**Параметры:**
- `user_id` (int): Уникальный идентификатор пользователя (id);
- `city` (str): Название города, который хотим отслеживать;
- `lat` (float): Широта города;
- `lon` (float): Долгота города.

**Пример запроса:**

`curl -X 'POST' "http://127.0.0.1:8000/track_city?user_id=1&city=Yakutsk&lat=62.0339&lon=129.7331"`

**Пример ответа:**

```
{
  "message": "Start weather tracking for Yakutsk"
}
```


## 5. Получение списка отслеживаемых городов:
**GET /tracked_cities** - Возвращает список всех городов, отслеживаемых пользователем.

**Параметры:**
- `user_id` (int): Уникальный идентификатор пользователя (id);


**Пример запроса:**

`curl "http://127.0.0.1:8000/tracked_cities?user_id=1"`

**Пример ответа:**

```
[
  "Yakutsk",
  "Chelyabinsk"
]
```

## 6. Получение данных о погоде в указанном городе:
**GET /city_weather** - Возвращает прогноз погоды (определенные параметры) для указанного города и времени.

**Параметры:**
- `user_id` (int): Уникальный идентификатор пользователя (id);
- `city` (str): Название доступного города для указанного пользователя;
- `time` (str): Время в формате `Europe/Moscow` (ISO 8601);
- `parameters` (str, optional): Список параметров погоды. Доступные параметры (по умолчанию): `temperature_2m,windspeed_10m,relative_humidity_2m,precipitation`


**Пример запроса:**

`curl "http://127.0.0.1:8000/city_weather?user_id=1&city=Yakutsk&time=2025-01-18T10%3A00&parameters=temperature_2m%2Cwindspeed_10m%2Crelative_humidity_2m%2Cprecipitation"`

**Пример ответа:**

```
{
  "temperature_2m": -39.3,
  "windspeed_10m": 3.4,
  "relative_humidity_2m": 61,
  "precipitation": 0
}
```


# Дополнительные методы API (опционально)

## 7. Получение содержимого базы данных:
**GET /database** - Возвращает содержимое базы данных (всех пользователей, города, прогноз погоды для отслеживаемых городов).

**Пример запроса:**

`curl "http://127.0.0.1:8000/database"`

**Пример ответа:**

```
{
  "1": {
    "username": "Danila",
    "tracked_cities": {
      "Yakutsk": {
        "latitude": 62.0339,
        "longitude": 129.7331,
        "weather": {
          "time": "2025-01-18T20:15",
          "interval": 900,
          "temperature": -40.2,
          "windspeed": 3.2,
          "winddirection": 243,
          "is_day": 0,
          "weathercode": 2
        },
        "last_updated": "2025-01-18T20:15:06.643775"
      },
      "Chelyabinsk": {
        "latitude": 55.154,
        "longitude": 61.4291,
        "weather": {
          "time": "2025-01-18T20:15",
          "interval": 900,
          "temperature": -13.4,
          "windspeed": 7,
          "winddirection": 215,
          "is_day": 0,
          "weathercode": 1
        },
        "last_updated": "2025-01-18T20:15:06.894639"
      }
    }
  }
}
```


## 8. Сброс базы данных:
**POST /reset_database** - Позволяет очистить всю базу данных и удалить все зарегистрированные данные о пользователях.


**Пример запроса:**

`curl -X POST "http://127.0.0.1:8000/reset_database"`

**Пример ответа:**

```
{
  "message": "Database has been reset"
}
```

# Обновление данных в фоновом режиме

- Метод `scheduled_weather_updates` позволяет автоматически обновлять данные о погоде каждые 15 минут (`asyncio.sleep(900)`);
- Асинхронная задача управляется при помощи `asyncio.create_task()`

# Тестирование через Swagger UI

После запуска скрипта `python3 script.py`, можно открыть в браузере адрес:
`http://127.0.0.1:8000/docs` и провести тестирование работы API. 
Помимо этого, можно:
- Посмотреть все доступные методы и их параметры;
- Увидеть, как выглядият запросы и ответы, без написания кода (без использования `curl`).





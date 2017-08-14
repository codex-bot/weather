import requests

from weather.config import CITIES_COLLECTION_NAME, OPENWEATHER_API_KEY
from .base import CommandBase


class CommandWeather(CommandBase):

    def get_current_weather(self, id):
        try:
            response = requests.get("http://api.openweathermap.org/data/2.5/weather?id={}&appid={}".format(
                id,
                OPENWEATHER_API_KEY
            ))

            if response.status_code == 200:
                data = response.json()
                city = data['name']
                temp = int(float(data['main']['temp']) - 273.15)
                weather = data['weather'][0]['description']
                humidity = int(data['main']['humidity'])
                return temp, weather, humidity, city

        except Exception as e:
            self.sdk.log("Error: {}".format(e))
        return 0

    def get_forecast(self, id, period):
        try:
            response = requests.get(
                "http://api.openweathermap.org/data/2.5/forecast/daily?id={}&appid={}&cnt={}".format(
                    id,
                    OPENWEATHER_API_KEY,
                    period
                ))

            if response.status_code == 200:
                data = response.json()
                city = data['city']['name']

                forecast = []
                for weather in data['list']:
                    day = {
                        'temp': int(float(weather['temp']['day']) - 273.15),
                        'weather': weather['weather'][0]['description'],
                        'humidity': weather['humidity'],
                    }
                    forecast.append(day)
                return city, forecast

        except Exception as e:
            self.sdk.log("Error: {}".format(e))
        return 0

    async def __call__(self, payload):
        self.sdk.log("/weather handler fired with payload {}".format(payload))

        registered_city = self.sdk.db.find_one(CITIES_COLLECTION_NAME, {'chat': payload['chat']})

        if not registered_city:
            message = "Firstly choose your city: /city <CITY_ID>\nList of available cities is here: /cities"
        else:

            if payload['command'] == "weather":
                temp, weather, humidity, city = self.get_current_weather(registered_city['city_id'])
                if temp:
                    message = "Temperature for {} is {}°С\n{}, humidity is {}%".format(city, temp, weather, humidity)
                else:
                    message = "API error."

            else:
                period = 3
                if "rain10" in payload['command']:
                    period = 10

                city, forecast = self.get_forecast(registered_city['city_id'], period)
                message = "Forecast for {} days ({}) is:\n".format(period, city)
                for day in forecast:
                    message += "{}°С, {}, humidity is {}%\n".format(day['temp'], day['weather'], day['humidity'])

        await self.sdk.send_text_to_chat(
            payload["chat"],
            message
        )

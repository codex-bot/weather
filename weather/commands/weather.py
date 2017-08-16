import requests
import emoji
from datetime import datetime

from weather.config import CITIES_COLLECTION_NAME, OPENWEATHER_API_KEY
from .base import CommandBase


class CommandWeather(CommandBase):

    def parse_weather_condition(self, desc):
        cond = {
            'clear sky': ':sun:',
            'few clouds': ':partly_sunny:',
            'scattered clouds': ':cloud:',
            'broken clouds': ':cloud:',
            'shower rain': ':thunder_cloud_and_rain:',
            'rain': ':cloud_with_rain:',
            'thunderstorm': ':cloud_with_lightning_and_rain:',
            'snow': ':cloud_with_snow:',
            'mist': ':fog:',
            'Thunderstorm': ':thunder_cloud_and_rain:',
            'Drizzle': ':cloud_with_lightning_and_rain:',
            'Rain': ':cloud_with_rain:',
            'Snow': ':cloud_with_snow:',
            'Atmosphere': ':foggy:',
            'Clear': ':sun:',
            'Clouds': ':cloud:',
            'Extreme': ':tornado:',
            'Additional': ':leaf_fluttering_in_wind:'
        }
        return emoji.emojize(cond.get(desc, ''))

    def load_forecast(self, city_id, period, daily=''):
        """

        :param city_id: City ID according to the http://bulk.openweathermap.org/sample/city.list.json.gz
        :param period: Number of 3-hour intervals. period=8 for a day, period=40 for 5 days.
        :return: None or <tuple>(<Dict> City info, <List> forecasts for each 3-hour period).
        """
        try:
            response = requests.get("http://api.openweathermap.org/data/2.5/forecast{}?id={}&appid={}&cnt={}".format(
                daily,
                city_id,
                OPENWEATHER_API_KEY,
                period
            ))
            if response.status_code == 200:
                data = response.json()
                city_info = data['city']
                forecast = data['list']
                return city_info, forecast

        except Exception as e:
            self.sdk.log("Error: {}".format(e))
        return None

    def get_daily_forecast(self, city_id):
        city_info, forecast = self.load_forecast(city_id, 8)
        data = []
        for weather in forecast[:4]:
            temp = int(float(weather['main']['temp']) - 273.15)
            temp = "{}{}".format("-" if temp < 0 else "+", temp)
            data.append({
                'time': datetime.fromtimestamp(int(weather['dt'])).strftime('%H') + ":00",
                'temp': temp,
                'desc': weather['weather'][0]['description'],
                'emoji': self.parse_weather_condition(weather['weather'][0]['description'])
            })

        message = "{}, {}°С {}\n\n".format(
            city_info['name'],
            data[0]['temp'],
            data[0]['emoji'])

        message += '\n'.join([
            '{} – {}°С {} {}'.format(weather['time'], weather['temp'], weather['emoji'], weather['desc'])
            for weather in data
        ])

        return message

    def get_weekly_forecast(self, city_id, days):
        city_info, forecast = self.load_forecast(city_id, days, '/daily')
        data = []
        for weather in forecast:
            temp = int(float(weather['temp']['day']) - 273.15)
            temp = "{}{}".format("-" if temp < 0 else "+", temp)
            data.append({
                'time': datetime.fromtimestamp(int(weather['dt'])).strftime('%d.%m'),
                'temp': temp,
                'desc': weather['weather'][0]['description'],
                'emoji': self.parse_weather_condition(weather['weather'][0]['main'])
            })

        message = "{}, {}°С {}\n\n".format(
            city_info['name'],
            data[0]['temp'],
            data[0]['emoji'])

        message += '\n'.join([
                                 '{} – {}°С {} {}'.format(weather['time'], weather['temp'], weather['emoji'], weather['desc'])
                                 for weather in data
                                 ])

        return message

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
                # temp, weather, humidity, city = self.get_current_weather(registered_city['city_id'])
                # if temp:
                #     message = "Temperature for {} is {}°С\n{}, humidity is {}%".format(city, temp, weather, humidity)
                # else:
                #     message = "API error."
                message = self.get_daily_forecast(registered_city['city_id'])
            else:
                period = 3
                if "rain10" in payload['command']:
                    period = 10
                message = self.get_weekly_forecast(registered_city['city_id'], period)
                # city, forecast = self.get_forecast(registered_city['city_id'], period)
                # message = "Forecast for {} days ({}) is:\n".format(period, city)
                # for day in forecast:
                #     message += "{}°С, {}, humidity is {}%\n".format(day['temp'], day['weather'], day['humidity'])

        await self.sdk.send_text_to_chat(
            payload["chat"],
            message
        )

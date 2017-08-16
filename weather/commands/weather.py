import requests
import emoji
from datetime import datetime

from config import CITIES_COLLECTION_NAME, OPENWEATHER_API_KEY
from .base import CommandBase


class CommandWeather(CommandBase):

    @staticmethod
    def parse_weather_condition(desc):
        """
        Translate weather description to emoji.
        :param desc: weather condition
        :return: unicode emoji
        """
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
        Load forecast for period specified.
        :param city_id: City ID according to the http://bulk.openweathermap.org/sample/city.list.json.gz
        :param period: Number of 3-hour or daily intervals.
        :param daily: Empty for 3-hour intervals and '/daily' for daily intervals.
        :return: None or <tuple>(<Dict> City info, <List> forecasts for each period).
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
        """
        Return message with forecast for the next 9 hours.
        :param city_id: City ID according to the http://bulk.openweathermap.org/sample/city.list.json.gz
        :return: message for Telegram
        """
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
        """
        Return message with forecast for the next $days days.
        :param city_id: City ID according to the http://bulk.openweathermap.org/sample/city.list.json.gz
        :param days: number of days
        :return: message for Telegram
        """
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

    async def __call__(self, payload):
        self.sdk.log("/weather handler fired with payload {}".format(payload))

        registered_city = self.sdk.db.find_one(CITIES_COLLECTION_NAME, {'chat': payload['chat']})

        if not registered_city:
            message = "Firstly choose your city: /city <CITY_ID>\nList of available cities is here: /cities"
        else:

            if payload['command'] == "weather":
                message = self.get_daily_forecast(registered_city['city_id'])
            else:
                period = 3
                if "rain10" in payload['command']:
                    period = 10
                message = self.get_weekly_forecast(registered_city['city_id'], period)

        await self.sdk.send_text_to_chat(
            payload["chat"],
            message
        )

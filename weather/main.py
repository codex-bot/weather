from commands.help import CommandHelp
from sdk.codexbot_sdk import CodexBot
from config import APPLICATION_TOKEN, APPLICATION_NAME, DB, URL, SERVER

from weather.commands.cities import CommandCities
from weather.commands.city import CommandCity
from weather.commands.weather import CommandWeather


class Weather:

    def __init__(self):

        self.sdk = CodexBot(APPLICATION_NAME, SERVER['host'], SERVER['port'], db_config=DB, token=APPLICATION_TOKEN)

        self.sdk.log("Weather module initialized")

        self.sdk.register_commands([
            ('weather_help', 'help', CommandHelp(self.sdk)),
            ('weather', 'weather', CommandWeather(self.sdk)),
            ('cities', 'cities', CommandCities(self.sdk)),
            ('city', 'city', CommandCity(self.sdk)),
            ('rain3', 'rain3', CommandWeather(self.sdk)),
            ('rain10', 'rain10', CommandWeather(self.sdk))
        ])

        self.sdk.set_routes([])
        self.sdk.start_server()


if __name__ == "__main__":
    weather = Weather()

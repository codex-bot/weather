from commands.help import CommandHelp
from sdk.codexbot_sdk import CodexBot
from config import APPLICATION_TOKEN, APPLICATION_NAME, DB, URL, SERVER


class Weather:

    def __init__(self):

        self.sdk = CodexBot(APPLICATION_NAME, SERVER['host'], SERVER['port'], db_config=DB, token=APPLICATION_TOKEN)

        self.sdk.log("Notify module initialized")

        self.sdk.register_commands([
            ('weather', 'Weather позволит вам отправлять сообщения в чат POST запросом', CommandHelp(self.sdk)),
            ('weather_help', 'help', CommandHelp(self.sdk))
        ])

        self.sdk.set_routes([])

        self.sdk.start_server()


if __name__ == "__main__":
    weather = Weather()

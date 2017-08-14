from weather.config import CITIES_COLLECTION_NAME
from .base import CommandBase


class CommandWeather(CommandBase):

    async def __call__(self, payload):
        self.sdk.log("/weather handler fired with payload {}".format(payload))

        registered_city = self.sdk.db.find_one(CITIES_COLLECTION_NAME, {'chat': payload['chat']})

        if not registered_city:
            message = "Firstly choose city: /city <CITY_ID>\nList of available cities is here: /cities"
        else:
            message = "Weather for city {} is {}"

        await self.sdk.send_text_to_chat(
            payload["chat"],
            message
        )

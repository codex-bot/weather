from weather.config import CITIES_COLLECTION_NAME
from .base import CommandBase


class CommandCities(CommandBase):

    async def __call__(self, payload):
        self.sdk.log("/cities handler fired with payload {}".format(payload))
        await self.sdk.send_text_to_chat(
            payload["chat"],
            "You can download full cities list by the link: http://bulk.openweathermap.org/sample/city.list.json.gz\n" \
            "Saint-Petersburg ID is 498817, Moscow - 5601538"
        )

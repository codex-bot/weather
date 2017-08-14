from weather.config import CITIES_COLLECTION_NAME
from .base import CommandBase


class CommandCity(CommandBase):

    async def __call__(self, payload):
        self.sdk.log("/city handler fired with payload {}".format(payload))

        if not payload['params']:
            message = "Enter city ID\n\nExample: '/city 498817'"
        else:
            city_id = int(payload['params'])

            registered_city = self.sdk.db.find_one(CITIES_COLLECTION_NAME, {'chat': payload['chat']})
            if not registered_city:
                self.sdk.db.insert(CITIES_COLLECTION_NAME, {'chat': payload['chat'], 'city_id': city_id})
            else:
                self.sdk.db.update(CITIES_COLLECTION_NAME,
                                   {'chat': payload['chat']},
                                   {'chat': payload['chat'], 'city_id': city_id}
                                   )
            message = "You choose city with ID = {}".format(city_id)

        await self.sdk.send_text_to_chat(
            payload["chat"],
            message
        )

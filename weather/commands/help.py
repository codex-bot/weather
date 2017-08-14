from .base import CommandBase


class CommandHelp(CommandBase):

    async def __call__(self, payload):
        self.sdk.log("/help handler fired with payload {}".format(payload))
        await self.sdk.send_text_to_chat(
            payload["chat"],
            "This application allows you to easily get notifications about weather in your region.\n\n"
            "/weather – get today weather\n"
            "/cities – available cities list\n"
            "/city <CITY_ID> – set current city\n"
            "/rain3 – get weather forecast for 3 days\n"
            "/rain10 – get weather forecast for 10 days\n"
        )

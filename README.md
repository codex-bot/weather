## How to create a new application for @codex_bot platform

This article is about new @codex_bot application development. Throughout this guide we build an application that can provide weather forecast for different periods of time.

For simplicity we use our modern SDK for Python (**link**). We also provide instructions how to run your own production-ready @codex_bot server.

Before start you need to run [@codex_bot Core](https://github.com/codex-team/codex.bot) (read [Developer's Guide](https://github.com/codex-team/codex.bot/wiki/Developer's-Guide)) or use our [@codex_bot](https://t.me/codex_bot)

If you are wondering, we have a lot of other useful @codex_bot [applications](https://github.com/codex-bot) to play with. Check our [landing](https://ifmo.su/bot) for the further information.

## Install necessary tools

1. Python v.3.5.3 can be downloaded by the link (https://www.python.org/downloads/release/python-353/). Just follow installation instructions. You can use newer versions if you need.
2. MongoDB (https://www.mongodb.com). Useful hint – you can run Mongo with the Docker. Just follow the instructions in the next section.
3. Install a virtual environment for Python `apt-get install virtualenv или pip install virtualenv`
4. Initialize a virtual environment with `virtualenv venv -p python3`.

### Docker support
You can skip this step if you don't need to run MongoDB in a Docker.
1. Create working directory `mkdir mongo`
2. Run `docker run -v mongo:/data/db -p 27017:27017 -d mongo`

## Prepare sources

The sources of our example application could be found in [repository](https://github.com/codex-bot/weather).
1. You can get them with `git clone https://github.com/codex-bot/weather weather`
2. Activate virtual environment `source ../venv/bin/activate`
3. `cd weather`
3. Install necessary packages `pip install -r requirements.txt`
4. `cd weather`
5. Copy sample config to the work config `cp config.py.sample config.py`

## Configuration

1. Invent a new unique application name and fill corresponding parameter **APPLICATION_NAME**
2. Write to your bot (if you are running @codex_bot Core by yourself) or to the [@codex_bot](t.me/codex_bot) the following command: `/newapp {unique name of app} {your host}`. You will get a token back. Copy this token to corresponding parameter **APPLICATION_TOKEN** in your **config.py**

## Try to run

Now, you can run weather application with `python main.py` command. If everything is all right, you will get back several debug messages from Core with the prefix __Received__

## How it works

In *main.py* there is an SDK initialization with values from the configuration file.
`self.sdk = CodexBot(APPLICATION_NAME, SERVER['host'], SERVER['port'], db_config=DB, token=APPLICATION_TOKEN)`

After that, method **register_commands** tells Core which commands should be redirected to your application (note: this commands might be unique!).
```
self.sdk.register_commands([
    ('weather_help', 'help', CommandHelp(self.sdk)),
    ('weather', 'weather', CommandWeather(self.sdk)),
    ('cities', 'cities', CommandCities(self.sdk)),
    ('city', 'city', CommandCity(self.sdk)),
    ('rain3', 'rain3', CommandWeather(self.sdk)),
    ('rain10', 'rain10', CommandWeather(self.sdk))
])
```

Handlers for each command are defined in **commands** directory. You can find imports in the beginning of the main.py script:
```
from commands.help import CommandHelp
from commands.cities import CommandCities
from commands.city import CommandCity
from commands.weather import CommandWeather
```

Our SDK invokes **__init__** method with **payload** parameter. Watch an example in the **commangs/cities.py** file:
```
class CommandCities(CommandBase):
    async def __call__(self, payload):
        self.sdk.log("/cities handler fired with payload {}".format(payload))
        await self.sdk.send_text_to_chat(
            payload["chat"],
            "...message here..."
        )
```
When user inputs `/cities` command in the telegram chat with bot, you'll receive a debug message with the payload into your terminal:
`
logging.py          :17                  debug() 	 /cities handler fired with payload {'command': 'cities', 'params': '', 'chat': 'RXRI6S0N', 'user': 'VZXTDQ44'}
`

#### Usage
- `/city <CITY_ID>` — setting up your location
- `/cities` — view cities list
- `/weather` — get current weather conditions

![](https://capella.pics/3ee93508-ef47-4c61-9c2f-988e2e6d9b93)

## Issues and improvements

Ask a question or report a bug on the [create issue page](https://github.com/codex-bot/weather/issues/new).

Know how to improve platform? [Fork it](https://github.com/codex-bot/weather) and send a pull request.

## About CodeX

We are small team of passionate web-developers consisting of IFMO University students and graduates located in St. Petersburg, Russia. Fell free to give us a feedback on  [team@ifmo.su](mailto:team@ifmo.su)

# P2HB

[![Discord Bots](https://top.gg/api/widget/818706022675120138.svg)](https://top.gg/bot/818706022675120138)

## Usage
Feel free to host your own instance of the bot, however, you will be missing out on the thousands of tags with useful information compiled users, and you will not be able to use the economy on the P2HB Offical Server.

## Running
While I would prefer if you just [added the main instance of the bot](https://discord.com/oauth2/authorize?client_id=818706022675120138&permissions=8&scope=bot) to your server, here is the setup process to run your own instance.

1. **Get Python 3.8 or higher**

This is required to run the bot.

2. **Set up venv**

Do `python3.8 -m venv venv`

3. **Install dependencies**

We use Poetry to manage dependencies. Make sure you have [Poetry](https://python-poetry.org/docs/) installed, and just run `poetry install`.

4. **Create the database in MongoDB**

Please refer to the [MongoDB website](https://docs.mongodb.com/manual/tutorial/getting-started/) to do this.

5. **Setup config**

Create a `config.py` file in root directory using the following template:

```py
import random

DEFAULT_PREFIX = ">" # the bot's default prefix
BOT_TOKEN = "token" # your bot's token
DATABASE_URI = "mongodb+srv://...url" # MongoDB URI, you can get this once you set it up
DATABASE_NAME = "name" # name of database
DBL_TOKEN = "" # Top.gg token - not required

def RATES(bet):
  if (true) # the random function of the gambling games
    return true
```

That's it! You should be ready to run the bot now. 

## Contributing
I am open to contributions: please make an issue first, and then go ahead and create a pull request if you want to tackle it yourself.

## Things to be worked on
- [ ] Automatic Collector/Shiny Hunt system
- [ ] Gym Badges/Leaders
- [ ] Refactor puzzle games 
- [ ] Add images-based puzzle guessing games
- [ ] Create command documentation
- [ ] Automatic Price Checker/Duelish Checker

## Credits
Parts of code are from the official server helper bot: https://github.com/poketwo/helper-bot.   
Assets and pokemon data are taken from official bot: https://github.com/poketwo/poketwo.

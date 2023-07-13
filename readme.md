## Information
WIP
## Project Structure

`./models/*`
> Tortoise-orm models of the bot, main processing methods and code base.

`./modules/*`
> Bot's "UI" and commands, as well as receiving events (f.e "on_message")

`.env` - **to be created**, environment variables.  
`.env.example` - example for `.env`

`config.py` - configuration file.  
`bot.py` - bot's class, basic functionality and set up.  
`database.py` - tortoise-orm set up.  
`utils.py` - utility functions.

`main.py` - main file. Start from there.
# (Inofficial) SWR1 Chart Bot

This is my first attempt to create a telegram bot. The work on this project is very experimental to get some knowledge
and insides into the used technologies. Currently the work on the Bot is still in progress and therefore I cannot
guarantee stable operation.

With the Bot you can search for titles, artists and placements of the SWR1 Charts 2019.
The easiest way to search for something is to do a fulltext search by sending a message to the bot.
Beyond that you can perfom special searches by using bot command. For a list of all available command
send /hilfe to the bot.


## Technology stack

- Telegram Bots (https://core.telegram.org/bots) and Bot API (https://core.telegram.org/bots/api)
- Azure Functions (as backend)
- Python 3.6.8 (requirement of Azure Functions)
- python-telegram-bot Module (https://python-telegram-bot.org/)

## Create a bot

To create a bot, you have to use a telegram bot called [BotFather](https://telegram.me/botfather). Theses are the commands
I used to create my Bot.

| command         | input values                                                                                                                                                                                                                             |
|-----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| /newbot         | name: SWR1 Hitparade <br> username: mySWR_Hit_Bot                                                                                                                                                                                        |
| /setdescription | Du willst wissen, wer Platz 100 in der Hitparade war oder wie viele Titel Queen in der Hitparade hatte. Dann bist Du hier genau richtig. Mit diesem Bot kannst Du nach Titeln, Künstlern und Platzierungen in der SWR1 Hitparade suchen. |
| /setcommands    | platz - Gesuchte Platzierung<br>titel - Name des gesuchten Titels<br>musiker - Musiker- oder Bandname<br>anzahl - Musiker- oder Bandname<br>10 - Anzeige der Top Ten                                                                     |

The newbot-command generates a token wich must be used, to identify the Bot in your code.

## Create Azure Functions App

### Create Ressource Group

`az group create --name TelegramBotGroup --location westeurope`

### Create storage account

`az storage account create --name todabotstorage --location westeurope --resource-group TelegramBotGroup --sku Standard_LRS`

### Create Function App

`az functionapp create --resource-group TelegramBotGroup --os-type Linux --consumption-plan-location westeurope  --runtime python --name swr1_hit_bot --storage-account todabotstorage`

### Publishing the App

`func azure functionapp publish swr1-hit-bot --build remote`

## Config of the Webhook

To make the Telegram Bot able to work with the Azure Function, you have to configure the bot to use webhooks (https://core.telegram.org/bots/api#setwebhook). The required step is to configure a URL where the bot can send his messages to. This configuration cannot be done with the BotFather, instead you have to use the API. I created a small python script using the python-telegram-bot module to do the configuration.

`import telegram`

`bot = telegram.Bot(token='<bot_token>')`

`bot.set_webhook(url='https://swr1-hit-bot.azurewebsites.net/api/hit_bot?code=<azure_function_code>')`

`info = bot.get_webhook_info()`

`print(info)`

## Disclaimer

This bot is a private project of myself and has nothing to do with the official SWR1 charts or the SWR1 radio station. 
import telegram

bot = telegram.Bot(token='1038979600:AAHj8l2WkmGO5zl8GzxsMagyyJgL6_7bfns')
bot.set_webhook(
    url='https://swr1-hit-bot.azurewebsites.net/api/hit_bot?code=VNz8eRAEXCWia/a3X5AQGIEQ4AEgCLLamS7A9QlULJxRmoozJhPDDg==')

info = bot.get_webhook_info()
print(info)

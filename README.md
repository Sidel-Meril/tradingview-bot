# Tradingview Bot

Bot for taking capture of graph in [Tradingview](tradingview.com)

## Description

Bot implemented with using headless Selenium Browser and [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)

[Implementation of capturing by Selenium](interfaces/tradingview/selenium.py)
[PostgreSQL DB operating](interfaces/postgres/operations.py)

## Getting Started

This bot was deployed to [Heroku](tradingview.com) so configurated regad to [Heroku Google Chrome Buildpack](https://github.com/heroku/heroku-buildpack-google-chrome)

### Dependencies

[Check requirements.txt](requirements.txt)
[Check config file](conf/config.py)

### Executing program

1. [Start bot in Telegram](t.me/ScreenshotBotMarket_bot)
2. Type /start
3. See the full list of commands (it also avaliable with /help)
4. Choose /request
5. Type pair listed in /listpairs
6. Wait for result while Heroku Selenium capturing website

![Screeshot](https://i.ibb.co/JRJY4cx/image.png)

## Help

Any questions user can add with /ask command in bot. 


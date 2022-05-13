import os

class LocalConfig:
    PORT = int(os.environ.get('PORT', '8443'))
    TOKEN = os.environ['TELEGRAM_TOKEN']
    HEROKU_PROJECT_LINK = 'https://murmuring-inlet-95645.herokuapp.com/'+TOKEN
    CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH')
    GOOGLE_CHROME_BIN = os.environ.get("GOOGLE_CHROME_BIN")
    DATABASE_URL = os.environ['DATABASE_URL']
    WORKERS = 30
    CONVERSATION_POINTS = {
    'PAY_RESPONSE':1,
    'ASK_RESPONSE':2,
    'ANSWER_RESPONSE':3,
    'WRITEALL_RESPONSE':4,
    'EDITTEXT_LABEL_REQUEST':5,
    'EDITTEXT_TEXT_RESPONSE':6,
    'EDITTEXT_TEXT_REQUEST':7,
    'GET_SCREENSHOT':9
    }

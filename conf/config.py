import os

class LocalConfig:
    PORT = int(os.environ.get('PORT', '8443'))
    DATABASE_URL = ''
    TOKEN = '5146455970:AAG5GBUq0Z_t8DdWbf3xDmv05CGj0WQ4Xng'
    HEROKU_PROJECT_LINK = ''
    CHROMEDRIVER_PATH = "D:\PyProjects\chromedriver_win32\chromedriver.exe"
    GOOGLE_CHROME_BIN = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    DATABASE_URL = 'postgres://phsiksrqngenoy:f7c9ca60d11cdd47b6c76bd479706be8183f57a08f0b552b210550d10b4e1596@ec2-18-214-134-226.compute-1.amazonaws.com:5432/d46les6a5j0asm'
    WORKERS = 10
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

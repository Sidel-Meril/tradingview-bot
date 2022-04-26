from interfaces.tradingview.selenium import ChromeDriver
from conf.config import LocalConfig

conf = LocalConfig()

def get_screenshot(symbol, interval, cookies):
    examp = ChromeDriver(conf.CHROMEDRIVER_PATH, conf.GOOGLE_CHROME_BIN)
    if next((False for item in examp.ranges.values() if interval in list(item.values())), True):
        return False
    link = 'https://www.tradingview.com/chart/?symbol={SYMBOL}&interval={interval}'.format(SYMBOL=symbol, interval=interval)
    image = examp.get(link, source = 'https://www.tradingview.com/', cookies = cookies)
    return image

def log_in(username, password):
    examp = ChromeDriver(conf.CHROMEDRIVER_PATH, conf.GOOGLE_CHROME_BIN)
    data = examp.log_in(username, password)
    return data
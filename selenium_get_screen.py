import json
from PIL import Image
from io import StringIO, BytesIO
import base64
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import random
from time import sleep, time
import os

from selenium.webdriver.common.by import By


class ChromeDriver:

    def _start(func):
        def secure(self, *args, **kwargs):
            self._create_driver()
            result = func(self,*args, **kwargs)
            try:
                # self.driver.close
                pass
            except:
                pass
            return result
        return secure

    def _check_exists(self,by, value):
        try:
            self.driver.find_element(by=by, value=value)
        except NoSuchElementException:
            return False
        return True

    def __init__(self, path, cookies_path, headless=True):
        "Initial param. for creating Chrome driver"

        self.user_agents = open(r'user-agents.txt','r').read().split('\n')
        self.executable_path = path
        self.headless = headless
        with open(r'data-ranges.json', 'r') as f:
            self.ranges = json.load(f)

    def _create_driver(self):
        if not getattr(self, 'driver', None):
            chromeOptions = webdriver.ChromeOptions()
            chrome_options = webdriver.ChromeOptions()
            # chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            self.driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),
                                      chrome_options=chrome_options)

            self.driver.header_overrides = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'DNT': '1'
            }
            self.driver.set_window_size(1280, 800)

    @_start
    def log_in(self, login_url, login_data, source):
        self.driver.get(login_url)
        self.driver.implicitly_wait(10)
        sing_in_by_email = self.driver.find_element(by=By.XPATH, value=".//span[@class='tv-signin-dialog__social tv-signin-dialog__toggle-email js-show-email']")
        sing_in_by_email.click()
        username = self.driver.find_element(by=By.XPATH, value=".//input[@name='username']")
        username.click()
        username.clear()
        username.send_keys(login_data['username'])
        self.driver.implicitly_wait(10)
        password = self.driver.find_element(by=By.XPATH, value=".//input[@name='password']")
        password.click()
        password.clear()
        password.send_keys(login_data['password'])
        log_in = self.driver.find_element(by = By.XPATH, value=".//span[@class='tv-button__loader']")
        log_in.click()
        self.driver.implicitly_wait(10)
        self.driver.get(source)
        self.driver.implicitly_wait(10)
        self.cookies=self.driver.get_cookies()

    @_start
    def get(self, url, source, range, cookies=False):
        self.cookies = [{'domain': '.tradingview.com', 'expiry': 1924905600, 'httpOnly': False, 'name': 'tv_ecuid', 'path': '/', 'secure': False, 'value': '8c297591-f2cb-4696-b803-8545450b2bef'},
                        {'domain': '.tradingview.com', 'httpOnly': False, 'name': 'etg', 'path': '/', 'secure': False, 'value': '8c297591-f2cb-4696-b803-8545450b2bef'},
                        {'domain':'.tradingview.com', 'httpOnly': False, 'name': 'png', 'path': '/', 'secure': False, 'value': '8c297591-f2cb-4696-b803-8545450b2bef'},
                        {'domain': '.tradingview.com', 'httpOnly': False, 'name': 'cachec', 'path': '/', 'secure': False, 'value': '8c297591-f2cb-4696-b803-8545450b2bef'},
                        {'domain': '.tradingview.com', 'expiry': 1656793930, 'httpOnly': True, 'name': 'sessionid',
'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': '0ly8z4zl9k0wgjwtmnyv5jkte7igtftt'},
                        {'domain': '.tradingview.com', 'expiry': 1679862726, 'httpOnly': True, 'name': 'device_t', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'ZzlFMkFnOjA.E27rTVW1-3J7hnrJOMnKN1kSQMONbYF3725x-QKNPmU'}]
        if cookies:
            self.driver.get(source)
            self.driver.implicitly_wait(10)
            for cookie in self.cookies:
                self.driver.add_cookie(cookie)

        # login_url = 'https://en.tradingview.com/accounts/signin/'
        # login_data = {
        #                  'username': os.environ['TRADE_LOGIN'],
        #                  'password': os.environ['TRADE_PASSWORD']
        #              }
        #
        # self.driver.get(login_url)
        # self.driver.implicitly_wait(10)
        # sing_in_by_email = self.driver.find_element(by=By.XPATH, value=".//span[@class='tv-signin-dialog__social tv-signin-dialog__toggle-email js-show-email']")
        # sing_in_by_email.click()
        # username = self.driver.find_element(by=By.XPATH, value=".//input[@name='username']")
        # username.click()
        # username.clear()
        # username.send_keys(login_data['username'])
        # self.driver.implicitly_wait(10)
        # password = self.driver.find_element(by=By.XPATH, value=".//input[@name='password']")
        # password.click()
        # password.clear()
        # password.send_keys(login_data['password'])
        # log_in = self.driver.find_element(by = By.XPATH, value=".//span[@class='tv-button__loader']")
        # log_in.click()
        # sleep(5)
        # print(len(self.driver.get_cookies()))
        # print(self.driver.get_cookies())

        self.driver.implicitly_wait(10)
        self.driver.get(url)
        self.driver.implicitly_wait(10)

        chat_window = self.driver.find_element(by=By.XPATH, value='.//div[@class="chart-container-border"]')
        while self._check_exists(By.XPATH, './/div[@class="chart-gui-wrapper"'):
            sleep(0.1)

        sleep(0.1)

        # while self._check_exists(By.XPATH, "////*[contains(text(), 'This website uses cookies')]"):
        #     sleep(0.1)
        "accept cookies"
        test_el =self.driver.find_element(by=By.XPATH, value="//*[contains(text(), 'This website uses cookies')]")
        print(self.driver.page_source)
        try:
            accept_window = self.driver.find_element(by=By.XPATH, value='//div[@class="main-content-x9aer5B8"]')
            accept_line = accept_window.find_element(by=By.XPATH, value='//div[@class="actions-x9aer5B8"]')
            print('accept for cookies found')
            accept = accept_line.find_elements(by=By.XPATH, value="//button")
            accept[-1].click()
            sleep(0.5)
        except Exception as e:
            print(e)
            pass


        sleep(0.1)

        # bio = BytesIO()
        # im = BytesIO()
        # bio.name = 'image.png'
        # im.save(bio, 'PNG')
        print('screen saved.')
        return chat_window.screenshot_as_png

def get_screenshot(symbol, interval):
    # examp = ChromeDriver(os.environ.get('CHROMEDRIVER_PATH'), 'cookie.dump', True)
    examp = ChromeDriver('chromedriver.exe', 'cookie.dump', True)
    if next((False for item in examp.ranges.values() if interval in list(item.values())), True):
        return False
    link = 'https://www.tradingview.com/chart/?symbol={SYMBOL}&interval={interval}'.format(SYMBOL=symbol, interval=interval)
    image = examp.get(link, source = 'https://www.tradingview.com/', range=interval)
    return image


if __name__ == "__main__":
    start = time()
    get_screenshot('BLZUSDT',"1")
    print(time()-start)
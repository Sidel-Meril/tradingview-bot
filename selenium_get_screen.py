import json
from PIL import Image
from io import StringIO, BytesIO
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import random
from time import sleep, time

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
        self.cookies = None

    def _create_driver(self):
        if not getattr(self, 'driver', None):
            chromeOptions = Options()
            chromeOptions.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
            chromeOptions.add_argument("--no-sandbox")
            chromeOptions.add_argument("--disable-setuid-sandbox")
            chromeOptions.add_argument("--disable-dev-shm-using")
            chromeOptions.add_argument("--disable-extensions")
            chromeOptions.add_argument("--disable-gpu")
            chromeOptions.add_argument("start-maximized")
            chromeOptions.add_argument("disable-infobars")
            if self.headless == True: chromeOptions.add_argument("--headless")

            self.driver = webdriver.Chrome(
                executable_path=self.executable_path, options=chromeOptions, service_args=["--verbose", "--log-path=qc1.log"])

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

        with open('cookie.dump','wb') as f:
            pickle.dump(self.cookies,f)

    @_start
    def get(self, url, source, range, cookies=False):
        if cookies:
            self.driver.get(source)
            self.driver.implicitly_wait(10)
            for cookie in self.cookies:
                self.driver.add_cookie(cookie)

        self.driver.get(url)
        self.driver.implicitly_wait(10)

        while self._check_exists(By.XPATH, "////*[contains(text(), 'This website uses cookies')]"):
            sleep(0.1)
        "accept cookies"
        try:
            accept_window = self.driver.find_element(by=By.XPATH, value='//div[@class="main-content-2gM8G-uJ"]')
            accept_line = accept_window.find_element(by=By.XPATH, value='//div[@class="actions-2gM8G-uJ"]')
            print('accept for cookies found')
            accept = accept_line.find_elements(by=By.XPATH, value="//button")
            accept[-1].click()
            sleep(0.5)
        except Exception as e:
            print(e)
            pass

        chat_window = self.driver.find_element(by=By.XPATH, value='.//div[@class="chart-container-border"]')
        while self._check_exists(By.XPATH, './/div[@class="chart-gui-wrapper"'):
            sleep(0.1)
        sleep(0.1)

        # bio = BytesIO()
        # im = BytesIO()
        # bio.name = 'image.png'
        # im.save(bio, 'PNG')
        print('screen saved.')
        return chat_window.screenshot_as_png

def get_screenshot(symbol, interval):
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
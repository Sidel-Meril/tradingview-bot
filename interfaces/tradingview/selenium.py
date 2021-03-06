import json
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
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
                self.driver.close
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

    def __init__(self, path, binary):
        "Initial param. for creating Chrome driver"

        self.user_agents = open(r'./interfaces/tradingview/user-agents.txt','r').read().split('\n')
        self.executable_path = path
        self.binary_location = binary
        with open(r'./interfaces/tradingview/data-ranges.json', 'r') as f:
            self.ranges = json.load(f)

    def _create_driver(self):
        if not getattr(self, 'driver', None):
            chrome_options = webdriver.ChromeOptions()
            chrome_options.binary_location = self.binary_location
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            self.driver = webdriver.Chrome(executable_path=self.executable_path,
                                      chrome_options=chrome_options)

            self.driver.header_overrides = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'DNT': '1'
            }
            self.driver.set_window_size(2000, 800)

    @_start
    def log_in(self, username, password):
        login_url = 'https://en.tradingview.com/accounts/signin/'
        login_data = {
                         'username': username,
                         'password': password
                     }
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
        sleep(30)
        self.driver.implicitly_wait(10)
        return self.driver.get_cookies()

    @_start
    def get(self, url, source, cookies):
        self.driver.get(source)
        self.driver.implicitly_wait(10)
        for cookie in cookies:
            self.driver.add_cookie(cookie)

        self.driver.implicitly_wait(10)
        self.driver.get(url)
        self.driver.implicitly_wait(10)

        chat_window = self.driver.find_element(by=By.XPATH, value='.//div[@class="chart-container-border"]')
        while len(self.driver.find_elements(By.XPATH, './/div[@class="chart-toolbar chart-controls-bar"]')) == 0:
            pass
        sleep(5)
        "accept cookies"

        try:
            accept_window = self.driver.find_elements(by=By.XPATH, value="//button")
            button = list(filter(lambda element: 'Accept all' in element.get_attribute("innerHTML"), accept_window))
            print('accept for cookies found')
            button = button[0]
            button.click()
            while button.get_attribute("innerHTML") in self.driver.page_source:
                pass
        except Exception as e:
            print(e)

        print('screen saved.')
        return chat_window.screenshot_as_png


import os
import uuid
from random import uniform
# from subprocess import CREATE_NO_WINDOW

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import requests
from time import sleep
from pytz import timezone
from datetime import datetime, timedelta

from selenium.webdriver.support.wait import WebDriverWait

from main.g_spreadsheets import get_spreadsheet_id, get_service, get_data_from_sheet, get_range, add_text_to_sheet
from main.models import WorkTable
from main.save_data import save_json, get_json_data_from_file
from webparserapp.settings import setup

WINDOW_SIZE = "1920,1080"
CHROMEDRIVER_PATH = os.path.normpath(os.path.join(os.getcwd(), 'chromedriver', "chromedriver.exe")) \
    if setup.DEV else '/usr/local/bin/chromedriver'


def get_request_data(url: str, random_wait: tuple = (.01, .05)):
    """Receiving data on request with a random time delay,
    a random user agent and a proxy. There is also a time limit for receiving a request."""
    data_ = None
    # 10 попыток запросов на сервер с временной отсрочкой сменой ip и user-agent
    for i in range(5):
        sleep(uniform(*random_wait))
        # choice proxy
        proxy_ = None
        if proxy_:
            prx = {
                'http': 'http://' + proxy_,
                'https': 'http://' + proxy_,
            }
        else:
            prx = None
        # choice user agent
        u_agent_ = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2740.77 Safari/537.36'
        u_agent = {
            'user-agent': u_agent_,
            'accept': '*/*'
        }
        try:
            data_ = request_data(url, u_agent, prx)
        except Exception as e:
            print('get_request_data', f'{str(e)}')
        finally:
            if data_ is not None and data_.status_code == 200:
                data_.encoding = 'utf-8'
                break
    return data_


def request_data(url, headers=None, proxies=None, timeout=None):
    """Receiving data on request with a user agent, proxy.
    There is also set a time limit for receiving a request."""
    r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
    return r


def get_tab_data(driver):
    waiting_for_element(driver, (By.XPATH, '//div[@id="speed-index"]/div/div[2]'), 120)
    index = -1
    while index == -1:
        sleep(2)
        els = driver.find_elements(By.XPATH, '//div[@id="speed-index"]/div/div[2]')
        print('els len speed:', len(els))
        info = []
        for i, el in enumerate(els):
            text = el.text.strip().split(' ')[0]
            info.append(text)
            if text != '':
                index = i
        print('els text:', info)
    speed = els[index].text.strip().split(' ')[0]
    waiting_for_element(driver, (By.XPATH, '//div[@id="performance"]/div[1]/div[1]/div[1]/a/div[2]'), 120)
    index = -1
    while index == -1:
        sleep(2)
        els = driver.find_elements(By.XPATH, '//div[@id="performance"]/div[1]/div[1]/div[1]/a/div[2]')
        print('els len perf:', len(els))
        info = []
        for i, el in enumerate(els):
            text = el.text
            info.append(text)
            if text != '':
                index = i
        print('els text:', info)
    performance = els[index].text
    print('speed, performance:', [speed, performance])
    return speed, performance


def waiting_for_element(driver, element, wait_time):
    try:
        WebDriverWait(driver, wait_time).until(EC.presence_of_element_located(
            element))
    except Exception as e:
        print('WebDriver waiting_for_element', 'element timeout exceeded', str(e))


class Parser:
    def __init__(self, bot_id=None, name=None):
        super(Parser, self).__init__()
        spreadsheet, is_run = self.check_db()
        self.is_run = is_run
        self.id = uuid.uuid4() if bot_id is None else bot_id
        self.parser_name = name
        self.spreadsheet_link = spreadsheet
        self.spreadsheet_id = get_spreadsheet_id(spreadsheet)
        self.g_service = None

    def __del__(self):
        print(f'instance {self.id} - deleted')

    @classmethod
    def check_db(cls, spreadsheet=None):
        try:
            obj = WorkTable.objects.all()[0]
            if spreadsheet:
                obj.spreadsheet = spreadsheet
                obj.save()
        except Exception as e:
            print(str(e))
            if spreadsheet:
                obj = WorkTable(spreadsheet=spreadsheet, is_run=False)
                obj.save()
            else:
                return None, False
        return obj.spreadsheet, obj.is_run

    @classmethod
    def start(cls):
        try:
            obj = WorkTable.objects.all()[0]
            obj.is_run = True
            obj.save()
            return True
        except Exception as e:
            print(str(e))
            return False

    @classmethod
    def stop(cls):
        try:
            obj = WorkTable.objects.all()[0]
            obj.is_run = False
            obj.save()
            return True
        except Exception as e:
            print(str(e))
            return False

    @property
    def instance_id(self):
        return str(self.id)

    @property
    def name(self):
        return self.parser_name

    @property
    def spreadsheet(self):
        return self.spreadsheet_link

    def job(self):
        if not self.is_run:
            return
        t_zone = timezone('Europe/Moscow')
        time = t_zone.localize(datetime.now()).strftime("%b %d %Y %H:%M:%S")
        result = [time]
        print(result)
        urls = ['https://yandex.ru', 'https://google.ru']
        url_ = 'https://pagespeed.web.dev'
        service = Service(CHROMEDRIVER_PATH)
        # service.creationflags = CREATE_NO_WINDOW
        u_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                  'Chrome/98.0.4758.102 Safari/537.36 OPR/84.0.4316.21 '
        options = webdriver.ChromeOptions()
        options.add_argument('user-agent=' + u_agent)
        options.add_argument('headless')
        options.add_argument("--window-size=%s" % WINDOW_SIZE)
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(service=service, options=options)
        for url in urls:
            try:
                driver.get(url_)
                waiting_for_element(driver, (By.XPATH, '//input'), 60)
                el = driver.find_element(By.XPATH, '//input')
                action = webdriver.ActionChains(driver)
                action.send_keys_to_element(el, url).pause(uniform(.1, .5)) \
                    .send_keys_to_element(el, Keys.ENTER).perform()
                speed_, performance_ = '', ''
                for i in range(10):
                    waiting_for_element(driver, (By.XPATH, '//div[@aria-labelledby="mobile_tab"]'), 120)
                    sleep(5)
                    els = driver.find_elements(By.XPATH, '//div[@aria-labelledby="mobile_tab"]')
                    el = els[0]
                    print('els len:', len(els))
                    speed, performance = get_tab_data(el)
                    speed_ = speed if speed != '' else speed_
                    performance_ = performance if performance != '' else performance_
                    if speed_ != '' and performance_ != '':
                        break
                    sleep(uniform(0.1, 0.5))
                    driver.refresh()
                result.extend([speed_, performance_])

                speed_, performance_ = '', ''
                for i in range(10):
                    sleep(uniform(0.1, 0.5))
                    driver.refresh()
                    sleep(1)
                    driver.find_element(By.XPATH, '//*[@id="desktop_tab"]').click()
                    waiting_for_element(driver, (By.XPATH, '//div[@aria-labelledby="desktop_tab"]'), 120)
                    sleep(5)
                    el = driver.find_elements(By.XPATH, '//div[@aria-labelledby="desktop_tab"]')[0]
                    speed, performance = get_tab_data(el)
                    speed_ = speed if speed != '' else speed_
                    performance_ = performance if performance != '' else performance_
                    if speed_ != '' and performance_ != '':
                        break
                result.extend([speed_, performance_])
            except Exception as e:
                print(str(e))
        driver.quit()
        print(result)
        col_num = len(urls) * 4 + 2
        data, row_count = self.get_table_data()
        if row_count == 0:
            row1 = ['pagespeed.web.dev']
            for url in urls:
                row1.append('Мобильные устройства')
                row1.append(url)
                row1.append('Компьютер')
                row1.append(url)
            row2 = ['']
            for url in urls:
                row2.append('Speed Index')
                row2.append('Производительность')
                row2.append('Speed Index')
                row2.append('Производительность')
            header = [row1, row2]
            range_ = get_range([1, 1], [col_num, 2])
            add_text_to_sheet(self._get_g_service(), self.spreadsheet_id, header, range_, 'ROWS')
            row_count += 2
        range_ = get_range([1, row_count + 1], [col_num, row_count + 1])
        print(range_)
        add_text_to_sheet(self._get_g_service(), self.spreadsheet_id, [result], range_, 'ROWS')
        json_data = get_json_data_from_file('result_data/json/result.json')
        print('json data', json_data)
        if json_data:
            json_data.append(result)
        else:
            json_data = [result]
        print('json data', json_data)
        save_json(json_data, root_folder='result_data', folder='json')

    def _get_g_service(self):
        if self.g_service is None:
            self.g_service = get_service()
        return self.g_service

    def get_table_data(self):
        data = get_data_from_sheet(self._get_g_service(), self.spreadsheet_id, range_='A1:B', major_dimension='ROWS')
        rows = data.get('values')
        row_count = len(rows) if rows else 0
        print('table data:', data)
        print('row count: ', row_count)
        return data, row_count



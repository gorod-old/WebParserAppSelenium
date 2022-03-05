import os
import uuid
from random import uniform
# from subprocess import CREATE_NO_WINDOW

from bs4 import BeautifulSoup as Bs
from selenium import webdriver

import requests
from time import sleep

from selenium.webdriver.chrome.service import Service

from main.g_spreadsheets import get_spreadsheet_id, get_service, get_data_from_sheet, get_range, add_text_to_sheet
from main.models import WorkTable
from main.save_data import save_json
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
        result = []
        service = Service(CHROMEDRIVER_PATH)
        # service.creationflags = CREATE_NO_WINDOW

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument("--window-size=%s" % WINDOW_SIZE)
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(service=service, options=options)

        driver.get('https://www.instagram.com/support_point/')

        print(driver.title)
        result.append(driver.title)
        driver.quit()
        save_json(result, root_folder='result_data', folder='json')

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


class ParserAutoStart:
    def __init__(self, spreadsheet):
        super(ParserAutoStart, self).__init__()
        self.id = uuid.uuid4()
        self.parser_name = 'autostart 1'
        self.spreadsheet_link = spreadsheet
        self.spreadsheet_id = get_spreadsheet_id(spreadsheet)
        self.g_service = None

    def __del__(self):
        print(f'instance {self.id} - deleted')

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
        data, row_count = self.get_table_data()
        for i in range(row_count):
            row = data.get('values')[i]
            url = row[0]
            if 'https://' in url:
                r = get_request_data(url)
                print(r.status_code)
                if r and r.status_code == 200:
                    soup = Bs(r.text, 'html.parser')
                    row = []
                    title = None
                    try:
                        title = soup.select(
                            '#container > div.product-detail__same-part-kt.same-part-kt > div > '
                            'div.same-part-kt__header-wrap.hide-mobile > h1')[0].text.strip()
                    except Exception as e:
                        print(str(e))
                    row.append(title)
                    price_txt = None
                    try:
                        price_txt = soup.select(
                            '#infoBlockProductCard > div.same-part-kt__price-block > '
                            'div > div > p > span')[0].text.strip()
                    except Exception as e:
                        print(str(e))
                    price = ''
                    if price_txt:
                        for ch in price_txt:
                            if ch.isdigit():
                                price += ch
                    row.append(price)
                    range_ = get_range([2, i + 1], [4, i + 1])
                    print(range_)
                    add_text_to_sheet(self._get_g_service(), self.spreadsheet_id, [row], range_, 'ROWS')

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



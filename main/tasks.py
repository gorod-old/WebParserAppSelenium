from celery import shared_task

from main.parser import Parser, ParserAutoStart
from main.save_data import get_json_data_from_file


@shared_task
def run_pars():
    parser = Parser()
    print('spreadsheet:', parser.spreadsheet)
    print('is run:', parser.is_run)
    if parser.is_run:
        parser.job()


@shared_task
def run_pars_on_background(spreadsheet):
    parser = ParserAutoStart(spreadsheet)
    print('spreadsheet:', parser.spreadsheet)
    parser.job()


@shared_task
def process_data():
    path = 'result_data/json/result.json'
    data = get_json_data_from_file(path)
    # process data and save in spreadsheet >>>
    print(data)

from django.http import HttpResponseNotFound, HttpResponseRedirect, JsonResponse

from django.urls import reverse

from main.base import get_site_name, parse_json_payload
from main.exceptions import PayloadException
from main.forms import ParserStartForm
from main.g_spreadsheets import check_spreadsheet, get_credentials_email
from main.parser import Parser
from user_auth.base import check_auth
from webparserapp.settings import setup


# Create your views here.

@check_auth
def index(request):
    spreadsheet, is_run = Parser.check_db()
    form = ParserStartForm(initial={'spreadsheet': spreadsheet})
    context = {
        'title': f'{get_site_name()} - Home Page',
        'page_title': get_site_name(),
        'subtitle': setup.PROJ_SUBTITLE,
        'user_pk': request.user.pk,
        'spreadsheet': '' if not spreadsheet else spreadsheet,
        'is_run': is_run,
        'form': form
    }
    template = 'main/index.html'
    return context, template


def home(request):
    return HttpResponseRedirect(reverse('index'))


def run_parser(request):
    # GET POST DATA WITH TELETHON --->
    try:
        parser_name, phone, spreadsheet, channel = \
            parse_json_payload(request.body, 'parser_name', 'phone', 'spreadsheet', 'channel')
    except PayloadException as e:
        return e.to_response()

    spreadsheet_check = check_spreadsheet(spreadsheet)
    if spreadsheet_check is None:
        context = {
            'info': 'run_parser',
            'success': False,
            'message': "Can't access Google Spreadsheet, please make sure your Spreadsheet link is correct and you've "
                       "granted edit access at: ",
            'link': f"<a id='parser-link' style='color: #55a889; max-width: 100%; overflow-wrap: break-word;'>"
                    f"{get_credentials_email()}</a>"
        }
        return JsonResponse(context)

    spreadsheet, is_run = Parser.check_db(spreadsheet)
    if not is_run:
        info = 'start parser'
    else:
        info = 'update parser'
    success = Parser.start()
    exception = None
    # try:
    #     Parser().job()
    # except Exception as e:
    #     exception = str(e)
    return JsonResponse({'info': info, 'success': success, 'exception': exception})


def stop_parser(request):
    success = Parser.stop()
    return JsonResponse({'info': 'stop parser', 'success': success})


def page_not_found(request, exception):
    return HttpResponseNotFound(f'<h1>Page Not Found</h1><p>{str(exception)}</p>')

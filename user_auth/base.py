import json

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from ipware import get_client_ip

from user_auth.exceptions import PayloadException


def process_user_ip(request):
    ip, is_routable = get_client_ip(request)
    if ip is None:
        print("Unable to get the client's IP address")
    else:
        print(ip)
        if is_routable:
            print("The client's IP address is publicly routable on the Internet")
        else:
            print("The client's IP address is private")
    return ip


def _check_user_auth(user):
    auth = False
    context = {}
    print('user obj is_auth: ', user)
    if user.is_authenticated:
        auth = True
        context.update({'username': user.username})
        context.update({'user_pk': user.pk})
    return auth, context


def check_auth(func):
    """check user auth decorator"""
    def wrapper(*args, **kwargs):
        request = args[0]
        auth, context = _check_user_auth(request.user)
        context_, template = func(*args, **kwargs)
        context.update(context_)
        if not auth:
            return HttpResponseRedirect(reverse('login'))
        return render(request=request, template_name=template, context=context)

    return wrapper


def parse_json_payload(body, *keys):
    """
    Parse request.body and yield lookup values
    """
    try:
        raw_payload = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PayloadException("Cant decode body '%s'\n%s" % (body, exc))
    try:
        payload = json.loads(raw_payload)
    except (ValueError, TypeError) as exc:
        raise PayloadException("Can't load JSON from raw payload '%s'\n%s" % (raw_payload, exc))
    for key in keys:
        yield payload.get(key)

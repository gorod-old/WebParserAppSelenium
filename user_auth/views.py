from django.contrib.auth import login, authenticate, logout
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from main.base import get_site_name
from user_auth.base import process_user_ip, parse_json_payload
from user_auth.exceptions import PayloadException
from user_auth.tokens import account_activation_token
from user_auth.forms import LoginForm, SignUpForm
from user_auth.models import *
from webparserapp.settings import setup
from .tasks import send_acc_verification_mail


def entry(request):
    form = LoginForm()
    signup_form = SignUpForm()
    redirect = request.META.get('HTTP_REFERER')
    if redirect is None or '/activate' in redirect:
        redirect = 'home/'
    context = {
        'title': f'{get_site_name()} - Entry',
        'form': form,
        'signup_form': signup_form,
        'redirect': redirect,
        'signup': setup.SIGNUP
    }
    return render(request, 'user_auth/entry.html', context=context)


def create_user(request):
    # GET POST DATA --->
    try:
        username, first_name, last_name, email, password, confirm, privacy_check = \
            parse_json_payload(request.body, 'username', 'first_name', 'last_name', 'email', 'password',
                               'confirm', 'privacy_check')
    except PayloadException as e:
        return e.to_response()

    response = {
        'created': False,
        'info': []
    }
    username_check = User.objects.filter(username=username)
    email_check = User.objects.filter(email=email)
    if len(username_check) > 0:
        response['info'].append('user with this name already exists')
    if len(email_check) > 0:
        response['info'].append('user with this email already exists')
    if confirm != password:
        response['info'].append('password confirmation does not match')
    if privacy_check == 'false':
        response['info'].append('privacy and term of use checkbox not checked')
    if len(response['info']) == 0:
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = False
        user.save()
        u_profile = UserProfile(user=user)
        u_profile.save()
        email_data = {
            'domain': get_current_site(request).domain,
            'user': str(user),
            'email': email,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        }
        send_acc_verification_mail.delay(email_data)  # celery task
        # send_account_verification_link(email_data)
        response['created'] = True
        response['info'].append('Your account has been created and an activation link has been sent to your email')
    return JsonResponse(response)


def activate_user(request):
    print('Account activation:')
    uidb64 = request.GET['uidb64']
    token = request.GET['token']
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # context = {'user_pk': user.pk if user else None}
    context = {}
    if user is not None and user.is_active:
        print('user:', user, 'is active: true')
        context.update({'success': True})
        context.update({'info': 'Your account is already activated'})
    elif user is not None and account_activation_token.check_token(user, token):
        print('user:', user, 'check token: true')
        user.is_active = True
        user.save()
        context.update({'success': True})
        context.update({'info': 'Account successfully activated'})
    else:
        print('user:', user, 'check token: false')
        context.update({'success': False})
        context.update({'info': 'Activation link is invalid!'})
    return render(request, 'user_auth/acc_activation.html', context=context)


def user_auth(request):
    ip = process_user_ip(request)
    # GET POST DATA --->
    try:
        username, password = parse_json_payload(request.body, 'username', 'password')
    except PayloadException as e:
        return e.to_response()

    obj, created = TemporaryBanIp.objects.get_or_create(
        defaults={
            'ip_address': ip,
            'time_unblock': timezone.now()
        },
        ip_address=ip
    )
    print('TemporaryBanIp - obj, created: ', obj, created)
    print('ban status: ', obj.status)
    response = {
        'passed': False,
    }
    # если IP заблокирован и время разблокировки не настало
    if obj.status is True and obj.time_unblock > timezone.now():
        if obj.attempts == 3 or obj.attempts == 6:
            # то открываем страницу с сообщением о блокировки на 15 минут при 3 и 6 неудачных попытках входа
            response.update({'info': 'Your IP has been banned for 15 minutes, need to wait a while.'})
            return JsonResponse(response)
        elif obj.attempts == 9:
            # или открываем страницу о блокировке на 24 часа, при 9 неудачных попытках входа
            response.update({'info': 'Your IP has been banned for 24 hours, need to wait a while.'})
            return JsonResponse(response)
    elif obj.status is True and obj.time_unblock < timezone.now():
        # если IP заблокирован, но время разблокировки настало, то разблокируем IP
        obj.status = False
        obj.save()

    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            response = {
                'passed': True,
                'info': 'User is active and logged in.',
                'redirect': f'parser-choice/',
            }
            obj.attempts = 0
            obj.save()
        else:
            response.update({'info': 'User profile deactivated.'})
    else:
        obj.attempts += 1
        if obj.attempts == 3 or obj.attempts == 6:
            obj.time_unblock = timezone.now() + timezone.timedelta(minutes=1)
            obj.status = True
        elif obj.attempts == 9:
            obj.time_unblock = timezone.now() + timezone.timedelta(minutes=1)
            obj.status = True
        elif obj.attempts > 9:
            obj.attempts = 1
        obj.save()

        def get_rem_attempts():
            td_list = [3, 6, 9]
            if obj.attempts in td_list:
                return 'You have been subject to a suspension penalty.'
            if obj.attempts < 3:
                return f'You have {3 - obj.attempts} attempts left before the time delay.'
            elif obj.attempts >= 6:
                return f'You have {9 - obj.attempts} attempts left before the time delay.'
            return f'You have {6 - obj.attempts} attempts left before the time delay.'

        response.update({'info': f'An incorrect username or password was entered. '
                                 f'{get_rem_attempts()}'})
    return JsonResponse(response)


def user_logout(request):
    logout(request)
    return JsonResponse({'logout': True})


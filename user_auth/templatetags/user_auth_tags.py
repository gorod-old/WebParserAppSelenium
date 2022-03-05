from django import template
from django.forms import model_to_dict

from user_auth.base import _check_user_auth
from user_auth.models import *

register = template.Library()


@register.inclusion_tag('user_auth/tags/user_info.html')
def get_user_profile(user_pk):
    print('Get User Profile:', user_pk)
    user, auth, user_profile = None, False, None
    try:
        user = User.objects.get(pk=user_pk)
        auth, context = _check_user_auth(user)
        if auth:
            user_profile = UserProfile.objects.get(user=user)
            user_profile = model_to_dict(user_profile, fields=[field.name for field in user_profile._meta.fields])
            user_profile.update({'username': user.username})
    except Exception as e:
        print('get user info filed, ', str(e))
    if auth and not user_profile:
        user_profile = {'username': user.username}
    return {'user_profile': user_profile}


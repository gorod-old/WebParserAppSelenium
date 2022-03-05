from django import template
from django.conf import settings
from django.forms import model_to_dict

from main.models import SiteSettings
from user_auth.models import *

register = template.Library()


ALLOWABLE_VALUES = ("MEDIA_URL", )


@register.simple_tag
def settings_value(name):
    if name in ALLOWABLE_VALUES:
        return getattr(settings, name, '')
    return ''


@register.simple_tag
def site_info(field_name):
    response = None
    try:
        site = SiteSettings.objects.all()[0]
        site = model_to_dict(site, fields=[field.name for field in site._meta.fields])
        response = site[field_name]
    except Exception as e:
        print(f'main_tags.site_info: field name "{field_name}" not find, ', str(e))
    return response


from django.contrib import admin

# Register your models here.
from main.models import SiteSettings, WorkTable

admin.site.register(SiteSettings)
admin.site.register(WorkTable)

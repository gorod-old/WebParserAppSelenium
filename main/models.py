from django.contrib import admin
from django.db import models

# Create your models here.


class WorkTable(models.Model):
    spreadsheet = models.CharField(max_length=250, verbose_name='spreadsheet link')
    is_run = models.BooleanField(verbose_name='is_run')


class WorkTableAdmin(admin.ModelAdmin):
    list_display = ('spreadsheet', 'is_run')


class SiteSettings(models.Model):
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
        db_table = "main_site_settings"

    site_title = models.CharField(max_length=100, verbose_name='Site name', default='Django Project')
    logo = models.ImageField(upload_to=f'images/site settings/logo/', null=True, blank=True, verbose_name='Logo')
    favicon = models.ImageField(upload_to=f'images/site settings/favicon/', null=True, blank=True,
                                verbose_name='Fav Icon')


class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_title', 'logo', 'favicon')

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False

    def has_add_permission(self, request):
        # Disable add
        return False

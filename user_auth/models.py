from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class UserProfile(models.Model):
    # This field is required:
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # Other fields here:
    icon = models.ImageField('User Avatar', upload_to=f'images/user_avatars/',
                             default='images/user_avatars/user-img.png', null=True)
    lang = models.CharField('Language', max_length=100, default='en', null=True)

    def __str__(self):
        return self.user.username


class TemporaryBanIp(models.Model):
    class Meta:
        verbose_name = 'Temporarily banned IPs'
        verbose_name_plural = 'Temporarily banned IPs'
        db_table = "TemporaryBanIp"

    ip_address = models.GenericIPAddressField("IP адрес")
    attempts = models.IntegerField("Неудачных попыток", default=0)
    time_unblock = models.DateTimeField("Время разблокировки", blank=True)
    status = models.BooleanField("Статус блокировки", default=False)

    def __str__(self):
        return self.ip_address


class TemporaryBanIpAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'status', 'attempts', 'time_unblock')
    search_fields = ('ip_address',)

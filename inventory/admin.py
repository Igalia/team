from django.contrib import admin
from django.db.models.functions import Lower

from inventory.models import DeviceType, Device, DeviceModel


@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    ordering = (Lower('name'), )


@admin.register(DeviceModel)
class DeviceAdmin(admin.ModelAdmin):
    ordering = ('brand', 'model_name')


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'owner')

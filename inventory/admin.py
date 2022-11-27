from django.contrib import admin
from django.db.models.functions import Lower

from inventory.models import DeviceType, Device


@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    ordering = (Lower('name'), )


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'owner')
    ordering = ('brand', 'model_name')

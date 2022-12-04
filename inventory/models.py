from django.db import models

from people.models import Person


class DeviceType(models.Model):
    """
    General type of an inventory item, such as "Laptop", "Workstation", "Printer", etc.
    """

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class DeviceModel(models.Model):
    """
    Defines the core properties that make sense for any device.
    """
    type = models.ForeignKey(DeviceType, null=True, blank=True, on_delete=models.SET_NULL)
    # Brand name (or "make"), such as "Dell" or "HP".
    brand = models.CharField(max_length=50)
    # Market model name, such as "XPS 15 9550" or "Pavilion 15".
    model_name = models.CharField(max_length=50)
    # Code that helps identifying the model when looking for support, such as "P54G" or "eg2022na".
    # The format depends on the manufacturer.
    model_code = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return "{brand} {name}".format(brand=self.brand, name=self.model_name)


class Device(models.Model):
    """
    A single item in the inventory of the company.

    Properties of particular devices should be stored in a separate model associated with the DeviceType instance.
    """
    model = models.ForeignKey(DeviceModel, on_delete=models.PROTECT)

    assignee = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL)

    serial_number = models.CharField(max_length=50, null=True, blank=True)
    manufacture_year = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.owner:
            return "{owner}'s {name}".format(owner=self.owner.login, name=str(self.model))
        return str(self.model)

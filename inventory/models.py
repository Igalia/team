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
    STATUS_ALLOCATED = "allocated"
    STATUS_AVAILABLE = "available"
    STATUS_BROKEN = "broken"
    STATUS_DISCARDED = "discarded"
    STATUS_RETURNED = "returned"
    STATUS_STORED = "stored"
    STATUS_CHOICES = [
        (STATUS_ALLOCATED, "Allocated"),
        (STATUS_AVAILABLE, "Available"),
        (STATUS_BROKEN, "Broken"),
        (STATUS_DISCARDED, "Discarded"),
        (STATUS_RETURNED, "Returned to Customer"),
        (STATUS_STORED, "Stored"),
    ]

    # Identity data of this device.  Once these fields are set, they should be immutable.

    model = models.ForeignKey(DeviceModel, on_delete=models.PROTECT)
    manufacture_year = models.IntegerField(null=True, blank=True)
    serial_number = models.CharField(max_length=50, null=True, blank=True)
    # Date when the device was purchased (literally, when the invoice was issued).
    purchase_date = models.DateField(blank=True, null=True)
    # Date when the device was registered in the inventory.
    creation_date = models.DateTimeField(auto_now_add=True, blank=True)

    # Status

    last_update_date = models.DateTimeField(auto_now=True, blank=True)

    assignee = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(
        max_length=max(len(x) for (x, _) in STATUS_CHOICES),
        choices=STATUS_CHOICES,
        default=STATUS_ALLOCATED,
    )
    location = models.CharField(max_length=100, null=True, blank=True)

    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.assignee:
            return "{assignee}'s {device}".format(assignee=self.assignee.login, device=str(self.model))
        return str(self.model)


class DeviceLaptop(models.Model):
    """
    Extends the generic Device with properties specific to laptops.
    """

    SIZE_13 = "13"
    SIZE_14 = "14"
    SIZE_15 = "15"
    SIZE_16 = "16"
    SIZE_17 = "17"
    SIZE_CHOICES = [
        (SIZE_13, "13\""),
        (SIZE_14, "14\""),
        (SIZE_15, "15\""),
        (SIZE_16, "16\""),
        (SIZE_17, "17\""),
    ]

    device = models.OneToOneField(Device, on_delete=models.PROTECT)

    screen_diagonal_in = models.CharField(
        max_length=max(len(x) for (x, _) in SIZE_CHOICES),
        choices=SIZE_CHOICES)
    screen_width_px = models.PositiveIntegerField()
    screen_height_px = models.PositiveIntegerField()

    cpu = models.CharField(verbose_name="CPU", max_length=100, blank=True)
    ram = models.CharField(verbose_name="RAM", max_length=100, blank=True)
    storage = models.CharField(max_length=100, blank=True)


class DeviceWorkstation(models.Model):
    """
    Extends the generic Device with properties specific to workstations.
    """

    device = models.OneToOneField(Device, on_delete=models.PROTECT)

    cpu = models.CharField(verbose_name="CPU", max_length=100, blank=True)
    ram = models.CharField(verbose_name="RAM", max_length=100, blank=True)
    storage = models.CharField(max_length=100, blank=True)

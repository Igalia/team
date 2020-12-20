from django.db import models
from django.utils.translation import ugettext_lazy as _


class Level(models.Model):
    name = models.CharField(max_length=20)
    value = models.IntegerField(unique=True)

    class Meta:
        verbose_name = _('Level')
        verbose_name_plural = _('Levels')

    def __str__(self):
        return self.name


class Person(models.Model):
    # Unique ID of the person in the system.
    login = models.CharField(max_length=30, unique=True)
    # Level in the company hierarchy.
    level = models.ForeignKey(Level, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.login

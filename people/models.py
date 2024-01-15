import datetime
import os
from uuid import uuid4

from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from team import settings


def mangle_filename(instance, filename):
    """Generates a UUID-based unique hard-to-guess filename

    :param instance: the DB model that this path is generated for
    :param filename: the "original" filename (normally comes from the uploaded file)
    :return: path to the new location within `MEDIA_ROOT`

    The `instance` may have a `STORAGE_PATH` attribute that will be used as a prefix of the resulting path
    """
    name, ext = os.path.splitext(filename)
    new_path = os.path.join(instance.STORAGE_PATH if hasattr(instance, "STORAGE_PATH") else "",
                            '{}{}'.format(uuid4().hex, ext))
    # UUID is generated based on current time and 14 bit random component as parts, so the collision is not likely.
    # In an unlikely event of the collision, just bail out.
    assert not os.path.exists(new_path)
    return new_path


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
    # Full name.
    full_name = models.CharField(max_length=100, null=True)
    # Date when this person joined the company.
    join_date = models.DateField(null=True)
    # Level in the company hierarchy.
    level = models.ForeignKey(Level, on_delete=models.PROTECT, null=True)

    teams = models.ManyToManyField('Team', blank=True)

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('People')

    def __str__(self):
        return '{login}@ {name}'.format(login=self.login, name=self.full_name)


class PersonalData(models.Model):
    """
    Extended data about a person.
    """

    STORAGE_PATH = settings.PEOPLE_PERSONAL_DATA_STORAGE

    # Extends the Person model.
    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    # Geographical location in form of a query for the external locator service, like "London, United Kingdom".
    location_query = models.CharField(max_length=100, null=True, blank=True)
    # Timezone database name, like "Europe/Madrid".
    tz_name = models.CharField(max_length=30, default="Etc/UTC")
    # Typical hour of beginning the work.
    work_begin_time = models.TimeField(default=datetime.time(9, 00))
    # Typical hour of ending the work.
    work_end_time = models.TimeField(default=datetime.time(18, 00))
    # Person's avatar.
    avatar = models.ImageField(null=True, blank=True, upload_to=mangle_filename)

    class Meta:
        verbose_name = _('Personal data')
        verbose_name_plural = _('Personal data')

    def __str__(self):
        return str(self.person)


# noinspection PyUnusedLocal
@receiver(models.signals.pre_save, sender=PersonalData)
def delete_old_avatar(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_avatar = PersonalData.objects.get(pk=instance.pk).avatar
        # old_avatar can be None if it belongs to a new PersonalData that has just been created.
        # It should be deleted IFF it exists AND the new instance differs (that is, either is empty or points to another
        # file).
        if old_avatar and old_avatar.url and old_avatar != instance.avatar:
            old_avatar.delete(save=False)
    except PersonalData.DoesNotExist:
        pass


class Team(models.Model):
    """
    Team inside a company.

    Groups various things within the company, primarily people, but not only people.

    The name may be confusing because it clashes with the name of this entire project.  Sorry.
    """

    slug = models.SlugField(max_length=50, unique=True)
    # Arbitrary name of the team; however, it has some constraints.
    name = models.CharField(max_length=50, unique=True)
    # Arbitrary text describing the team.
    description = models.TextField(default='', blank=True)

    class Meta:
        verbose_name = _('Team')
        verbose_name_plural = _('Teams')

    def __str__(self):
        return self.name

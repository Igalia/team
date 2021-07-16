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

    teams = models.ManyToManyField('Team', blank=True)

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('People')

    def __str__(self):
        return self.login


class Team(models.Model):
    """
    Team inside a company.

    Groups people and projects.  Relations are many-to-many both times because it is possible for a person to be a
    member of more than a single team, and projects can be cross-team as well.

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

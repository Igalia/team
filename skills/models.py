from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from people.models import Person, Team

NOTABLE_INTEREST_THRESHOLD = 0.3
EXPERT_KNOWLEDGE_THRESHOLD = 0.2
HIGH_KNOWLEDGE_THRESHOLD = 0.4


class Category(models.Model):
    # Arbitrary name of the category.
    name = models.CharField(max_length=50, unique=True)
    # Which teams this category is defined for.
    teams = models.ManyToManyField(Team)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name


class Skill(models.Model):
    # Arbitrary name of the skill.
    name = models.CharField(max_length=50)
    # A skill belongs to the single Category.
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # Arbitrary text explaining the skill.
    description = models.TextField(default='', blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('name', 'category'), name='skill_name_unique_in_category'),
        ]
        verbose_name = _('Skill')
        verbose_name_plural = _('Skills')

    def __str__(self):
        return self.name


class PersonAssessment(models.Model):
    """
    Skill assessment of a person.

    Groups a set of Measurements linked to a Person at the certain date, which basically means recording answers to
    a set of questions like 'do you know it? would you like to know it?' asked to the person as a block (e.g., in form
    of a survey).
    """
    date = models.DateField()
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    latest = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('date', 'person'), name='one_assessment_per_day'),
            models.UniqueConstraint(fields=['person'], condition=Q(latest=True), name='one_latest_per_person')
        ]
        verbose_name = _('Assessment')
        verbose_name_plural = _('Assessments')

    def __str__(self):
        return '{person} at {date}'.format(person=self.person, date=self.date)


class Measurement(models.Model):
    KNOWLEDGE_NONE = 0
    KNOWLEDGE_LOW = 1
    KNOWLEDGE_MEDIUM = 2
    KNOWLEDGE_HIGH = 3
    KNOWLEDGE_EXPERT = 4
    KNOWLEDGE_CHOICES = (
        (KNOWLEDGE_NONE, _('No knowledge')),
        (KNOWLEDGE_LOW, _('Touched it while doing unrelated things')),
        (KNOWLEDGE_MEDIUM, _('Did minor things there')),
        (KNOWLEDGE_HIGH, _('Did major things there')),
        (KNOWLEDGE_EXPERT, _('Expert')),
    )

    INTEREST_NONE = 0
    INTEREST_LOW = 1
    INTEREST_MEDIUM = 2
    INTEREST_HIGH = 3
    INTEREST_EXTREME = 4
    INTEREST_CHOICES = (
        (INTEREST_NONE, _('No interest')),
        (INTEREST_LOW, _('I wouldn\'t mind working in this area')),
        (INTEREST_MEDIUM, _('I would like to work in this area')),
        (INTEREST_HIGH, _('I really want to work in this area')),
        (INTEREST_EXTREME, _('I am obsessed with it!')),
    )

    assessment = models.ForeignKey(PersonAssessment, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    knowledge = models.IntegerField(choices=KNOWLEDGE_CHOICES, default=KNOWLEDGE_NONE)
    interest = models.IntegerField(choices=INTEREST_CHOICES, default=INTEREST_NONE)


class Project(models.Model):
    """A project that has been evaluated.  Not necessarily the one that the team works on.
    """

    # Project name.
    name = models.CharField(max_length=50, verbose_name=_('Name'), unique=True)
    # Arbitrary text explaining the project.
    description = models.TextField(default='', verbose_name=_('Description'))
    # Date of the most recent evaluation.
    date = models.DateField(verbose_name=_('Last assessment'))
    # Whether this project has been worked on by the team.
    active = models.BooleanField(default=False, verbose_name=_('The team is/was working on it'))
    # Which teams this project is driven by.
    teams = models.ManyToManyField(Team)

    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.date = timezone.now()
        super().save(*args, **kwargs)


class ProjectFocusRecord(models.Model):
    """Marks one skill that the project focuses on.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('project', 'skill'), name='unique_skill_in_project')
        ]
        verbose_name = _('Project focus record')
        verbose_name_plural = _('Project focus records')

    def __str__(self):
        return _('{project} → {skill}').format(project=self.project.name, skill=self.skill.name)

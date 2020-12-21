from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from people.models import Person, Level


class Ballot(models.Model):
    # Who has created this ballot.
    creator = models.ForeignKey(Person, on_delete=models.PROTECT)
    # The essence of the ballot.
    question = models.CharField(max_length=100)
    # The details.
    description = models.TextField()
    # Minimal level required to see this ballot and vote in it.
    access_level = models.ForeignKey(Level, on_delete=models.PROTECT)
    # Whether this ballot is open, i.e., voters can see votes of others before casting their own vote.
    open = models.BooleanField(default=True)
    # Whether this ballot is active, i.e., the creator has pushed the Publish button, and people can see it and vote.
    active = models.BooleanField(default=False)
    # When this ballot has been created.
    created = models.DateTimeField()
    # When this ballot should end.
    deadline = models.DateTimeField()
    # Whether the ballot is over and should no longer be displayed to people.
    archived = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Ballot')
        verbose_name_plural = _('Ballots')

    def __str__(self):
        return '{date} by {author}: {title}'.format(date=self.created, author=self.creator, title=self.question)

    @property
    def overdue(self):
        return self.deadline >= timezone.now()


class Vote(models.Model):
    VOTE_YES = 'Y'
    VOTE_NO = 'N'
    VOTE_ABSTAIN = 'A'
    VOTE_LEAVE = 'L'
    VOTE_CHOICES = (
        (VOTE_YES, _('Yes')),
        (VOTE_NO, _('No')),
        (VOTE_ABSTAIN, _('Abstain')),
        (VOTE_LEAVE, _('On Leave')),
    )

    ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE)
    caster = models.ForeignKey(Person, on_delete=models.PROTECT)
    vote = models.CharField(choices=VOTE_CHOICES, max_length=1)
    comment = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('caster', 'ballot'), name='one_vote_per_ballot'),
        ]
        verbose_name = _('Vote')
        verbose_name_plural = _('Votes')

    @property
    def vote_as_string(self):
        for choice in Vote.VOTE_CHOICES:
            if self.vote == choice[0]:
                return choice[1]
        return _('UNKNOWN')

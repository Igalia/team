from django import forms

from people.models import Level
from .models import Vote, Ballot


class BallotForm(forms.ModelForm):
    """Creates or edits the ballot.

    This form is used by the ballots.views.new().
    """

    class Meta:
        model = Ballot
        fields = ('question', 'description', 'access_level', 'open', 'deadline')

    def __init__(self, *args, **kwargs):
        max_level = kwargs.pop('max_level')
        assert max_level >= 1, "The access level must not be less than 1!"

        super(BallotForm, self).__init__(*args, **kwargs)

        if max_level == 1:
            self.fields.pop('access_level')
        else:
            self.fields['access_level'].choices = ((l.value, l.name) for l in
                                                   Level.objects.filter(value__lte=max_level).order_by('value'))

        self.fields['open'] = forms.ChoiceField(choices=((True, 'Open'), (False, 'Secret')), widget=forms.Select())


class VoteForm(forms.ModelForm):
    """Records vote in a ballot.

    This form is used by the ballots.views.ballot().
    """

    class Meta:
        model = Vote
        fields = ('vote', 'comment')

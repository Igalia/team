from django import forms

from .models import Vote


class VoteForm(forms.ModelForm):
    """Records vote in a ballot.

    This form is used by the ballots.views.ballot().
    """

    class Meta:
        model = Vote
        fields = ('vote', 'comment')

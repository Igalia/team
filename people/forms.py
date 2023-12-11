from django import forms

from people.models import PersonalData
from skills.models import Contribution


class ContributionForm(forms.ModelForm):
    """Allows to edit personal contribution.

    Used by the people.add_or_edit_contribution view.
    """
    class Meta:
        model = Contribution
        fields = ('project', 'description')


class PersonalDataForm(forms.ModelForm):
    """Allows to edit personal details.

    Used by the people.render_person view.
    """
    class Meta:
        model = PersonalData
        fields = ('location_query', 'tz_name', 'work_begin_time', 'work_end_time')


class SearchForm(forms.Form):
    """Captures the login of a person to show.

    Used by the people.render_person view.
    """
    login = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Type to search'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        fields = ('login',)

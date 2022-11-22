from django import forms

from people.models import PersonalData


class SearchForm(forms.Form):
    """Captures the login of a person to show.

    This form is used by the people.person view to search people.
    """
    login = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Type to search'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        fields = ('login',)


class PersonalDataForm(forms.ModelForm):
    """Allows to edit personal details.

    Used by the people.person view.
    """
    class Meta:
        model = PersonalData
        fields = ('location_query', 'tz_name', 'work_begin_time', 'work_end_time')

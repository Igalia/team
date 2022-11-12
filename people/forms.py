from django import forms


class SearchForm(forms.Form):
    """Captures the login of a person to show.

    This form is used by the people.person view to search people.
    """
    login = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        fields = ('login',)

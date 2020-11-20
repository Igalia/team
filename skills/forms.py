from django import forms

from .models import Measurement


class MeasurementForm(forms.ModelForm):
    """Records levels of knowledge and interest for one skill.

    This form is used by the skills.assess view to render one line of the assessment form.
    """
    def __init__(self, *args, **kwargs):
        if 'initial' in kwargs:
            for field in ('title', 'category_title'):
                if field in kwargs['initial']:
                    setattr(self, field, kwargs['initial'][field])
        super().__init__(*args, **kwargs)

    class Meta:
        model = Measurement
        fields = ('skill', 'knowledge', 'interest')
        widgets = {'skill': forms.HiddenInput}

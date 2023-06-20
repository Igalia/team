from django import forms

from people.models import Team
from .models import Measurement, Project, ProjectFocusRecord


class MeasurementForm(forms.ModelForm):
    """Records levels of knowledge and interest for one skill.

    This form is used by the skills.assess view to render one line of the assessment form.
    """
    def __init__(self, *args, **kwargs):
        if 'initial' in kwargs:
            for field in ('title', 'category_title', 'separator'):
                if field in kwargs['initial']:
                    setattr(self, field, kwargs['initial'][field])
        super().__init__(*args, **kwargs)

    class Meta:
        model = Measurement
        fields = ('skill', 'knowledge', 'interest')
        widgets = {'skill': forms.HiddenInput}


class ProjectFocusRecordForm(forms.ModelForm):
    """
    Records entry of skill into the project focus.

    This form is used by the skills.assess_project view to render one line of the assessment form.
    """
    selected = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        if 'initial' in kwargs:
            for field in ('title', 'category_title'):
                if field in kwargs['initial']:
                    setattr(self, field, kwargs['initial'][field])
        super().__init__(*args, **kwargs)

    class Meta:
        model = ProjectFocusRecord
        fields = ('skill', 'selected')
        widgets = {'skill': forms.HiddenInput}


class ProjectForm(forms.ModelForm):
    """
    Records data on the project.

    This form is used by the skills.assess_project view to render the project fields.
    """
    class Meta:
        model = Project
        fields = ('name', 'description', 'active')


class PickTeamForm(forms.ModelForm):
    """
    Records selection of a team.

    This form is used by the skills.pick_teams view to render one line of the form.
    """
    selected = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        if 'initial' in kwargs:
            for field in ('id', 'name', 'team'):
                if field in kwargs['initial']:
                    setattr(self, field, kwargs['initial'][field])
        super().__init__(*args, **kwargs)

    class Meta:
        model = Team
        fields = ('selected', )

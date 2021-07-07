import copy

from django.contrib import messages
from django.forms import formset_factory
from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from common.auth import get_user_login
from people.models import Person

from . import forms, models
from .forms import ProjectForm
from .models import Measurement, PersonAssessment, Project, ProjectFocusRecord, Skill, \
    EXPERT_KNOWLEDGE_THRESHOLD, HIGH_KNOWLEDGE_THRESHOLD, NOTABLE_INTEREST_THRESHOLD


# noinspection PyUnresolvedReferences
def enumerate_skills(additional_fields=None):
    if additional_fields is None:
        additional_fields = {}

    def describe(skill):
        nonlocal current_category
        description = {'skill': skill.pk, 'title': skill.name}
        for key, value in additional_fields.items():
            description[key] = copy.copy(value)
        if current_category != skill.category:
            current_category = skill.category
            description['category_title'] = current_category.name
        return description

    # Holds status for describe().
    current_category = None

    form_data = [describe(s) for s in models.Skill.objects.order_by('category__name', 'name')]
    skills_index = {form_data[i]['skill']: i for i in range(len(form_data))}
    return form_data, skills_index


# ======================================================================================================================
# Views
# ======================================================================================================================


# noinspection PyUnresolvedReferences
def demand_vs_knowledge(request):
    all_projects = [{'project': p, 'skills': []} for p in Project.objects.all()]
    all_focus_records = [r for r in ProjectFocusRecord.objects.all()]

    project_index = {all_projects[i]['project']: i for i in range(len(all_projects))}

    skills_data, skills_index = enumerate_skills({'knowledge': [0 for _ in Measurement.KNOWLEDGE_CHOICES],
                                                  'interest': [0 for _ in Measurement.INTEREST_CHOICES]})

    latest_assessments = [a for a in PersonAssessment.objects.filter(latest=True)]

    for measurement in Measurement.objects.filter(assessment__in=latest_assessments):
        skill = skills_data[skills_index[measurement.skill.pk]]
        skill['knowledge'][measurement.knowledge] += 1
        skill['interest'][measurement.interest] += 1

    assessment_count = len(latest_assessments)
    expert_threshold = assessment_count * EXPERT_KNOWLEDGE_THRESHOLD
    high_threshold = assessment_count * HIGH_KNOWLEDGE_THRESHOLD
    interest_threshold = assessment_count * NOTABLE_INTEREST_THRESHOLD
    for skill in skills_data:
        skill['star_knowledge'] = (skill['knowledge'][Measurement.KNOWLEDGE_EXPERT] >= expert_threshold or
                                   skill['knowledge'][Measurement.KNOWLEDGE_HIGH] >= high_threshold)
        skill['knowledge'] = skill['knowledge'][1:]
        skill['star_interest'] = skill['interest'][Measurement.INTEREST_EXTREME] >= interest_threshold
        skill['interest'] = skill['interest'][1:]

    max_count = 0
    for focus_record in all_focus_records:
        skill_record = skills_data[skills_index[focus_record.skill.pk]]
        if 'count' not in skill_record:
            skill_record['count'] = 1
        else:
            skill_record['count'] += 1
        max_count = max(max_count, skill_record['count'])
        all_projects[project_index[focus_record.project]]['skills'].append(focus_record.skill)

    for skill_record in skills_data:
        skill_record['bar_length'] = skill_record['count'] / max_count * 80 if 'count' in skill_record else 0

    return render(request,
                  'skills/demand-vs-knowledge.html',
                  {'page_title': 'Demand versus knowledge',
                   'projects': [{'project': p['project'],
                                 'skills': all_projects[project_index[p['project']]]['skills']}
                                for p in all_projects],
                   'skills': skills_data,
                   'notable_interest_threshold': format(NOTABLE_INTEREST_THRESHOLD, ".0%"),
                   'expert_knowledge_threshold': format(EXPERT_KNOWLEDGE_THRESHOLD, ".0%"),
                   'high_knowledge_threshold': format(HIGH_KNOWLEDGE_THRESHOLD, ".0%")})


# noinspection PyUnresolvedReferences
def home(request):
    """Shows the current team stats on all skills.
    """

    skills_data, skills_index = enumerate_skills({'knowledge': [0 for _ in Measurement.KNOWLEDGE_CHOICES],
                                                  'interest': [0 for _ in Measurement.INTEREST_CHOICES]})

    latest_assessments = [a for a in PersonAssessment.objects.filter(latest=True)]

    for measurement in Measurement.objects.filter(assessment__in=latest_assessments):
        skill = skills_data[skills_index[measurement.skill.pk]]
        skill['knowledge'][measurement.knowledge] += 1
        skill['interest'][measurement.interest] += 1

    assessment_count = len(latest_assessments)
    expert_threshold = assessment_count * EXPERT_KNOWLEDGE_THRESHOLD
    high_threshold = assessment_count * HIGH_KNOWLEDGE_THRESHOLD
    interest_threshold = assessment_count * NOTABLE_INTEREST_THRESHOLD
    for skill in skills_data:
        skill['star_knowledge'] = (skill['knowledge'][Measurement.KNOWLEDGE_EXPERT] >= expert_threshold or
                                   skill['knowledge'][Measurement.KNOWLEDGE_HIGH] >= high_threshold)
        skill['star_interest'] = skill['interest'][Measurement.INTEREST_EXTREME] >= interest_threshold

        skill['knowledge'] = skill['knowledge'][1:]
        skill['interest'] = skill['interest'][1:]

    return render(request,
                  'skills/home.html',
                  {'page_title': 'Our skills', 'skills': skills_data,
                   'notable_interest_threshold': format(NOTABLE_INTEREST_THRESHOLD, ".0%"),
                   'expert_knowledge_threshold': format(EXPERT_KNOWLEDGE_THRESHOLD, ".0%"),
                   'high_knowledge_threshold': format(HIGH_KNOWLEDGE_THRESHOLD, ".0%")})


# noinspection PyUnresolvedReferences
def render_skill(request, skill_id):
    """Shows details for the single skill.
    """

    try:
        skill = Skill.objects.get(pk=skill_id)
    except Skill.DoesNotExist:
        raise Http404("Skill does not exist")

    latest_assessments = [a for a in PersonAssessment.objects.filter(latest=True).order_by('person__login')]
    people = [{'person': assessment.person} for assessment in latest_assessments]
    people_index = {people[i]['person'].login: i for i in range(len(people))}
    measurements = Measurement.objects.filter(assessment__in=latest_assessments, skill=skill)
    for measurement in measurements:
        people[people_index[measurement.assessment.person.login]]['measurement'] = measurement

    return render(request,
                  'skills/skill.html',
                  {'page_title': 'Skill: {}'.format(skill.name), 'skill': skill, 'people': people})


# noinspection PyUnresolvedReferences
def render_person(request, login):
    """Shows details for the single person.
    """

    try:
        person = Person.objects.get(login=login)
    except Person.DoesNotExist:
        raise Http404("Person does not exist")

    try:
        latest_assessment = PersonAssessment.objects.get(latest=True, person=person)
    except PersonAssessment.DoesNotExist:
        latest_assessment = None

    skills_data, skills_index = enumerate_skills()

    if latest_assessment is not None:
        for measurement in Measurement.objects.filter(assessment=latest_assessment):
            skills_data[skills_index[measurement.skill.pk]]['measurement'] = measurement

    return render(request,
                  'skills/person.html',
                  {'page_title': 'Member: {}'.format(person.login),
                   'person': person,
                   'latest_assessment': latest_assessment,
                   'skills': skills_data})


# noinspection PyUnresolvedReferences
def project_create_edit(request, project_id):
    """Shows the actual project form.
    """

    existing_project = Project.objects.get(pk=project_id) if project_id > 0 else None

    # noinspection PyPep8Naming
    MeasurementFormSet = formset_factory(forms.ProjectFocusRecordForm, extra=0)

    skills, index = enumerate_skills()

    if existing_project:
        for focus_record in ProjectFocusRecord.objects.filter(project=existing_project):
            skills[index[focus_record.skill.pk]]['selected'] = True

    project_form = ProjectForm(request.POST or None, instance=existing_project if existing_project else None)
    formset = MeasurementFormSet(request.POST or None, initial=skills)

    if request.method == 'POST':
        if not project_form.is_valid() or not formset.is_valid():
            # Our form doesn't have fields that could contain invalid values, so if we are here, something is seriously
            # broken.  Terminate.
            raise Exception('Oops')
        saved_project = project_form.save()
        ProjectFocusRecord.objects.filter(project=saved_project).delete()
        for form in formset:
            if form.cleaned_data['selected']:
                focus_record = ProjectFocusRecord(project=saved_project, skill=form.cleaned_data['skill'])
                focus_record.save()
        messages.success(request, 'Project saved')
        return HttpResponseRedirect(reverse('skills:project', args=[saved_project.pk]))

    return render(request,
                  'skills/project.html',
                  {'page_title': 'Project assessment', 'project_form': project_form,
                   'project_title': existing_project.title if existing_project else _('<New>'), 'formset': formset})


def project_new(request):
    """Shows the form to create a new project.
    """
    return project_create_edit(request, 0)


def project(request, project_id):
    """Shows the form to edit an existing project.
    """
    return project_create_edit(request, project_id)


# noinspection PyUnresolvedReferences
def projects(request):
    all_projects = [{'project': p, 'skills': []} for p in Project.objects.all()]
    all_focus_records = [r for r in ProjectFocusRecord.objects.all()]

    project_index = {all_projects[i]['project']: i for i in range(len(all_projects))}

    for focus_record in all_focus_records:
        all_projects[project_index[focus_record.project]]['skills'].append(focus_record.skill)

    return render(request,
                  'skills/projects.html',
                  {'page_title': 'Our projects',
                   'projects': [{'project': p['project'],
                                 'skills': all_projects[project_index[p['project']]]['skills']}
                                for p in all_projects]})


# noinspection PyUnresolvedReferences
def self_assess(request):
    """Shows and handles the person self assessment form.
    """

    # noinspection PyPep8Naming
    MeasurementFormSet = formset_factory(forms.MeasurementForm, extra=0)

    # Take the login from the basic auth header.
    user_login = get_user_login(request)

    try:
        person = Person.objects.get(login=user_login)
    except Person.DoesNotExist:
        person = Person(login=user_login)

    if request.method == 'POST':
        formset = MeasurementFormSet(request.POST)
        if not formset.is_valid():
            # Our form doesn't have fields that could contain invalid values, so if we are here, something is seriously
            # broken.  Terminate.
            raise Exception('Oops')

        if not person.pk:
            # This is a new person; we need to save it now so objects created below would refer to it.
            person.save()

        try:
            assessment = PersonAssessment.objects.get(date=timezone.now(), person=person)
            # There is an existing assessment for this date.
            # Removing all existing measurements before recording new ones.
            Measurement.objects.filter(assessment=assessment).delete()
        except PersonAssessment.DoesNotExist:
            # Creating a new assessment.  It will be the latest one now.
            PersonAssessment.objects.filter(person=person, latest=True).update(latest=False)
            assessment = PersonAssessment(date=timezone.now(), person=person, latest=True)
            assessment.save()

        for form in formset:
            measurement = Measurement(assessment=assessment,
                                      skill=form.cleaned_data['skill'],
                                      knowledge=form.cleaned_data['knowledge'],
                                      interest=form.cleaned_data['interest'])
            if measurement.knowledge != Measurement.KNOWLEDGE_NONE or measurement.interest != Measurement.INTEREST_NONE:
                measurement.save()
        messages.success(request, 'Thank you for your input!')
        return HttpResponseRedirect(reverse('skills:home'))
    else:
        skills, index = enumerate_skills()

        try:
            latest_assessment = PersonAssessment.objects.get(person=person, latest=True)
            for measurement in Measurement.objects.filter(assessment=latest_assessment):
                form = skills[index[measurement.skill.pk]]
                form['knowledge'] = measurement.knowledge
                form['interest'] = measurement.interest
        except PersonAssessment.DoesNotExist:
            latest_assessment = None

        formset = MeasurementFormSet(initial=skills)
        return render(request,
                      'skills/self-assess.html',
                      {'page_title': 'Self assessment', 'user_login': person.login, 'formset': formset,
                       'latest_assessment': latest_assessment})

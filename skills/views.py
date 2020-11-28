from django.forms import formset_factory
from django.http.response import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from common.auth import get_user
from people.models import Person

from . import forms, models
from .models import PersonAssessment, Measurement, Skill


def home(request):
    """Shows the current team stats on all skills.
    """

    def describe(skill):
        nonlocal current_category
        description = {'skill': skill.pk,
                       'title': skill.name,
                       'knowledge': [0 for i in Measurement.KNOWLEDGE_CHOICES],
                       'interest': [0 for i in Measurement.INTEREST_CHOICES]}
        if current_category != skill.category:
            current_category = skill.category
            description['category_title'] = current_category.name
        return description

    # Holds status for describe().
    current_category = None

    skills_data = [describe(s) for s in models.Skill.objects.order_by('category__name', 'name')]
    skills_index = {skills_data[i]['skill']: i for i in range(len(skills_data))}

    latest_assessments = [a for a in PersonAssessment.objects.filter(latest=True)]

    assessment_count = len(latest_assessments)

    for measurement in Measurement.objects.filter(assessment__in=latest_assessments):
        skill = skills_data[skills_index[measurement.skill.pk]]
        skill['knowledge'][measurement.knowledge] += 1
        skill['interest'][measurement.interest] += 1

    for skill in skills_data:
        skill['knowledge_accumulated'] = sum(
            (skill['knowledge'][i] * i for i in range(len(Measurement.KNOWLEDGE_CHOICES))))
        skill['knowledge_average'] = skill['knowledge_accumulated'] / assessment_count
        skill['interest_accumulated'] = sum(
            (skill['interest'][i] * i for i in range(len(Measurement.INTEREST_CHOICES))))
        skill['interest_average'] = skill['interest_accumulated'] / assessment_count
        if skill['knowledge'][Measurement.KNOWLEDGE_EXPERT] >= 2:
            skill['comment'] = '2 or more experts!'
        elif skill['knowledge_average'] > Measurement.KNOWLEDGE_MEDIUM:
            skill['comment'] = 'Average is above medium.'
        skill['knowledge'] = skill['knowledge'][1:]
        skill['interest'] = skill['interest'][1:]

    return render(request,
                  'skills/home.html',
                  {'page_title': 'Our skills', 'skills': skills_data})


def skill(request, skill_id):
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


def person(request, login):
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

    def describe(skill):
        nonlocal current_category
        description = {'skill': skill.pk,
                       'title': skill.name}
        if current_category != skill.category:
            current_category = skill.category
            description['category_title'] = current_category.name
        return description

    # Holds status for describe().
    current_category = None

    skills_data = [describe(s) for s in models.Skill.objects.order_by('category__name', 'name')]
    skills_index = {skills_data[i]['skill']: i for i in range(len(skills_data))}
    if latest_assessment is not None:
        for measurement in Measurement.objects.filter(assessment=latest_assessment):
            skills_data[skills_index[measurement.skill.pk]]['measurement'] = measurement

    return render(request,
                  'skills/person.html',
                  {'page_title': 'Member: {}'.format(person.login),
                   'person': person,
                   'latest_assessment': latest_assessment,
                   'skills': skills_data})


def assess(request):
    """Shows and handles the person assessment form.
    """

    def describe(skill):
        nonlocal current_category
        description = {'skill': skill.pk, 'title': skill.name}
        if current_category != skill.category:
            current_category = skill.category
            description['category_title'] = current_category.name
        return description

    # Holds status for describe().
    current_category = None

    # noinspection PyPep8Naming
    MeasurementFormSet = formset_factory(forms.MeasurementForm, extra=0)

    # Take the login from the basic auth header.
    user_login = get_user(request)

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
        return HttpResponseRedirect(reverse('skills:assess-done'))
    else:
        form_data = [describe(s) for s in models.Skill.objects.order_by('category__name', 'name')]
        skills_index = {form_data[i]['skill']: i for i in range(len(form_data))}
        try:
            latest_assessment = PersonAssessment.objects.get(person=person, latest=True)
            for measurement in Measurement.objects.filter(assessment=latest_assessment):
                form = form_data[skills_index[measurement.skill.pk]]
                form['knowledge'] = measurement.knowledge
                form['interest'] = measurement.interest
        except PersonAssessment.DoesNotExist:
            latest_assessment = None

        formset = MeasurementFormSet(initial=form_data)
        return render(request,
                      'skills/assess.html',
                      {'page_title': 'Self assessment', 'user_login': person.login, 'formset': formset,
                       'latest_assessment': latest_assessment})


def assess_done(request):
    return render(request, 'skills/assess-done.html', {'page_title': 'Saved!'})

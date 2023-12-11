from django.contrib import messages
from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import resolve, Resolver404, reverse
from django.utils.translation import gettext_lazy as _

from common.auth import get_user_login
from common.forms import make_readonly
from inventory.models import Device
from skills.models import Contribution
from .forms import ContributionForm, PersonalDataForm, SearchForm
from .models import Level, Person, PersonalData, Team


def add_or_edit_contribution(request, contribution_id):
    contribution = Contribution.objects.get(pk=contribution_id) if contribution_id > 0 else None
    can_edit = (contribution.person.login == get_user_login(request)) if contribution else True
    contribution_form = ContributionForm(request.POST or None, instance=contribution)
    if not can_edit:
        make_readonly(contribution_form)

    if can_edit and request.method == "POST":
        if not contribution_form.is_valid():
            messages.warning(request, _("Please fix the data!"))
        else:
            saved_contribution = contribution_form.save()
            messages.success(request, _("Contribution saved"))
            return HttpResponseRedirect(reverse("people:contribution", args=[saved_contribution.pk]))

    try:
        return render(request, "people/contribution.html", {
            "can_edit": can_edit,
            "contribution_form": contribution_form,
            "contribution_list_title": _("My contributions") if can_edit else _(
                "{person}'s contributions".format(person=contribution.person.login)),
            "contribution_title": contribution.project.name if contribution else _("<New>"),
            "person": contribution.person if contribution else Person.objects.get(login=get_user_login(request)),
        })
    except Person.DoesNotExist:
        raise Http404("User does not exist")


def new_contribution(request):
    return add_or_edit_contribution(request, 0)


def render_contribution(request, contribution_id):
    return add_or_edit_contribution(request, contribution_id)


def render_contributions(request, login):
    try:
        person = Person.objects.get(login=login)
        contributions = Contribution.objects.filter(person=person).order_by("project__name")
        return render(request, "people/contributions.html", {
            "can_edit": (login == get_user_login(request)),
            "person": person,
            "contributions": contributions
        })

    except Person.DoesNotExist:
        raise Http404("User does not exist")


def render_person(request, login):
    people = Person.objects.order_by('login')
    search_form = SearchForm(request.POST or None)

    try:
        if request.method == 'POST' and search_form.is_valid():
            return HttpResponseRedirect(reverse('people:person', args=[search_form.cleaned_data['login']]))

        person = Person.objects.get(login=login)
        try:
            personal_data = PersonalData.objects.get(person=person)
        except PersonalData.DoesNotExist:
            personal_data = PersonalData(person=person)
            personal_data.save()

        can_edit = (login == get_user_login(request))
        if can_edit:
            personal_data_form = PersonalDataForm(request.POST or None, instance=personal_data)
            if request.method == 'POST' and personal_data_form.is_valid():
                personal_data_form.save()
                return HttpResponseRedirect(reverse('people:person', args=[login]))

        context = {'can_edit': can_edit,
                   'inventory': Device.objects.filter(assignee=person),
                   'people': people,
                   'person': person,
                   'personal_data': personal_data,
                   'search_form': search_form}
        if can_edit:
            context['personal_data_form'] = personal_data_form

        return render(request, 'people/person.html', context)
    except Person.DoesNotExist:
        try:
            path = '/{login}/'.format(login=login)
            resolve(path)  # If this fails, it will raise Resolver404.  Otherwise we just redirect to that URL.
            return HttpResponseRedirect(path)
        except Resolver404:
            pass
        return render(request, 'people/person.html', {
            'person': None,
            'people': people,
            'search_form': search_form})


def picker(request):
    return render(request, 'people/picker.html', {
        "levels": Level.objects.order_by("id"),
        "people": Person.objects.order_by("login"),
    })


def render_team(request, team_slug):
    return render(request, "people/team.html", {
        "team": Team.objects.get(slug=team_slug),
    })


def render_teams(request):
    return render(request, "people/teams.html", {
        "teams": Team.objects.order_by("name"),
    })

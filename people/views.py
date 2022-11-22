from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, resolve, Resolver404

from common.auth import get_user_login

from .forms import SearchForm, PersonalDataForm
from .models import Person, PersonalData


def person(request, login):
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
                       'person': person,
                       'personal_data': personal_data,
                       'people': people,
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

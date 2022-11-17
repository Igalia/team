from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, resolve, Resolver404

from .forms import SearchForm
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
        return render(request,
                      'people/person.html',
                      {'found': True,
                       'person': person,
                       'personal_data': personal_data,
                       'people': people,
                       'search_form': search_form})
    except Person.DoesNotExist:
        try:
            path = '/{login}/'.format(login=login)
            resolve(path)  # If this fails, it will raise Resolver404.  Otherwise we just redirect to that URL.
            return HttpResponseRedirect(path)
        except Resolver404:
            pass
        return render(request, 'people/person.html', {
            'person': 'User not found',
            'people': people,
            'search_form': search_form})

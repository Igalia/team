from django.shortcuts import render
from django.http.response import Http404, HttpResponseRedirect
from django.urls import reverse, resolve, Resolver404

from .forms import SearchForm
from .models import Person


def person(request, login):
    try:
        search_form = SearchForm(request.POST or None)

        if request.method == 'POST' and search_form.is_valid():
            return HttpResponseRedirect(reverse('people:person', args=[search_form.cleaned_data['login']]))

        person = Person.objects.get(login=login)
        people = Person.objects.all()
        return render(request,
                      'people/person.html',
                      {'person': person,
                       'people': people,
                       'search_form': search_form})
    except Person.DoesNotExist:
        try:
            path = '/{login}/'.format(login=login)
            resolve(path)   # If this fails, it will raise Resolver404.  Otherwise we just redirect to that URL.
            return HttpResponseRedirect(path)
        except Resolver404:
            pass
        raise Http404("Person with id '{}' does not exist.".format(login))

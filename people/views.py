from django.shortcuts import render

from .models import Person, Level


def picker(request):
    return render(request, 'people/picker.html', {
        "levels": Level.objects.order_by("id"),
        "people": Person.objects.order_by("login"),
    })

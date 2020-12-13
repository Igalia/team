from django.http.response import Http404
from django.shortcuts import render

from common.auth import get_user_login
from people.models import Person
from ballots.forms import VoteForm
from ballots.models import Ballot, Vote


def get_user(request):
    # Take the login from the basic auth header.
    user_login = get_user_login(request)

    try:
        return Person.objects.get(login=user_login)
    except Person.DoesNotExist:
        raise Http404("User does not exist")


def home(request):
    """Shows the ballots available to the current user.
    """

    user = get_user(request)

    ballots = [b for b in Ballot.objects.filter(access_level__lte=user.level.value, archived=False).order_by('-deadline')]
    votes = Vote.objects.filter(ballot__in=ballots)
    votes_index = {v.ballot.pk: v.vote for v in votes}

    ballots_to_vote = []
    active_ballots = []
    for ballot in ballots:
        if ballot.pk in votes_index:
            active_ballots.append(ballot)
        else:
            ballots_to_vote.append(ballot)

    return render(request,
                  'ballots/home.html',
                  {'page_title': 'Our ballots',
                   'ballots_to_vote': ballots_to_vote,
                   'active_ballots': active_ballots,
                   'user': user})


def new(request):
    user = get_user(request)
    return render(request,
                  'ballots/new.html',
                  {'page_title': 'New ballot',
                   'user': user})


def ballot(request, ballot_id):
    """Shows details for the single skill.
    """

    try:
        ballot = Ballot.objects.get(pk=ballot_id)
    except ballot.DoesNotExist:
        raise Http404("ballot does not exist")

    user = get_user(request)
    if user.level.value < ballot.access_level.value:
        raise Http404("ballot does not exist")

    vote = None
    form = None
    try:
        vote = Vote.objects.get(ballot=ballot, caster=user)
    except Vote.DoesNotExist:
        form = VoteForm()

    if ballot.open or vote:
        votes = [p for p in Person.objects.filter(level__value__gte=ballot.access_level.value)]
    else:
        votes = None

    return render(request,
                  'ballots/ballot.html',
                  {'page_title': 'ballot: {}'.format(ballot.question),
                   'ballot': ballot,
                   'vote': vote,
                   'form': form,
                   'votes': votes,
                   'user': user})

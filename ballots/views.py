import collections

from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

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
    votes = Vote.objects.filter(ballot__in=ballots, caster=user)
    votes_index = {v.ballot.pk: v for v in votes}

    ballots_to_vote = []
    active_ballots = []
    for ballot in ballots:
        if ballot.pk in votes_index:
            active_ballots.append({'ballot': ballot, 'vote': votes_index[ballot.pk]})
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

    if request.method == 'POST':
        form = VoteForm(request.POST)
        if not form.is_valid():
            # Our form doesn't have fields that could contain invalid values, so if we are here, something is seriously
            # broken.  Terminate.
            raise Exception('Oops')

        vote = Vote(ballot=ballot, caster=user, vote=form.cleaned_data['vote'], comment=form.cleaned_data['comment'])
        vote.save()

        return HttpResponseRedirect(reverse('ballots:ballot', kwargs={'ballot_id': ballot_id}))

    our_vote = None
    form = None
    try:
        our_vote = Vote.objects.get(ballot=ballot, caster=user)
    except Vote.DoesNotExist:
        form = VoteForm()

    if ballot.open:
        votes = [v for v in Vote.objects.filter(ballot=ballot)]
        votes_index = {v.caster.pk: v for v in votes}
        people = [p for p in Person.objects.filter(level__value__gte=ballot.access_level.value)]
        votes = collections.defaultdict(list)
        comments = collections.defaultdict(list)
        pending = []
        for person in people:
            if person.pk not in votes_index:
                pending.append(person.login)
                continue
            v = votes_index[person.pk]
            votes[v.vote].append(person.login)
            if v.comment:
                comments[v.vote].append({'person': person, 'comment': v.comment})
        ballot_data = {}
        for vote, _ in Vote.VOTE_CHOICES:
            if not votes[vote]:
                continue
            ballot_data[vote] = {'count': len(votes[vote]),
                                 'people': ', '.join(votes[vote]),
                                 'comments': comments[vote]}
        all_votes = []
        titles = {c: v for (c, v) in Vote.VOTE_CHOICES}
        for code in ('Y', 'N', 'A'):
            if code in ballot_data:
                all_votes.append({'title': titles[code], 'votes': ballot_data[code]})
    else:
        all_votes = None

    return render(request,
                  'ballots/ballot.html',
                  {'page_title': 'ballot: {}'.format(ballot.question),
                   'ballot': ballot,
                   'our_vote': our_vote,
                   'form': form,
                   'all_votes': all_votes,
                   'pending': {
                       'count': len(pending),
                       'people': ', '.join(pending) if len(pending) > 1 else pending,
                   },
                   'user': user})


def retract_vote(request, ballot_id):
    """Erases the user's existing vote.
    """

    try:
        ballot = Ballot.objects.get(pk=ballot_id)
    except ballot.DoesNotExist:
        raise Http404("Ballot does not exist")

    user = get_user(request)
    if user.level.value < ballot.access_level.value:
        raise Http404("Ballot does not exist")

    try:
        our_vote = Vote.objects.get(ballot=ballot, caster=user)
        our_vote.delete()
        return HttpResponseRedirect(reverse('ballots:ballot', kwargs={'ballot_id': ballot_id}))
    except Vote.DoesNotExist:
        raise Http404("Vote does not exist")

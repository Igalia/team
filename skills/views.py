import copy

from django.conf import settings
from django.contrib import messages
from django.forms import formset_factory
from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.auth import get_user_login
from common.forms import make_readonly
from people.models import Person, Team
from . import forms
from .forms import ProjectForm
from .models import Measurement, PersonAssessment, Project, ProjectFocusRecord, Skill, \
    EXPERT_KNOWLEDGE_THRESHOLD, HIGH_KNOWLEDGE_THRESHOLD, NOTABLE_INTEREST_THRESHOLD

# Virtual team selector that shows data for all teams that the current user is in.
# Only recognised by the team selector view that redirects immediately.  Cannot be used as a fictive slug.
MY_TEAMS = '-'
# Virtual team selector that shows data for all teams in the company.
# Recognised as a fictive team slug and can be used in permanent URLs to all views that accept team slug.
ALL_TEAMS = '--'


def merge(x, y):
    """Compatibility function that merges two dictionaries.
    TODO: remove when we no longer need compatibility with 3.8.
    """
    z = x.copy()  # start with keys and values of x
    z.update(y)  # modifies z with keys and values of y
    return z


# noinspection PyUnusedLocal
def enable_projects(request):
    """
    Feature switch for "projects" which may be disabled.

    :param request: not used.
    :return: Whether project-related functionality should be exposed.
    """
    return getattr(settings, "SKILLS_ENABLE_PROJECTS", False)


def user_should_be_in_some_teams(strict):
    """
    Decorator for views that ensures that the current user belongs to at least one team.

    Some views do not have a team selector in their URL; they use user's teams instead.  Thus, they imply that the user
    belongs to at least one team.  For some of them, however, the 'current team' selected in the session is a valid
    substitute; for others, it is not.  Team diagrams are in the former group (anyone can browse data for any team), and
    assessment forms, both for people and for projects, are in the latter one: skills are bound to teams, therefore one
    cannot assess themselves if they do not belong to any team.

    This decorator wraps the view with logic that loads the current person and checks whether they belong to any teams.
    It also checks whether the current team is set in the session.  Depending on these checks and on the value of the
    |strict| parameter, it calls either the wrapped view or render_pick_teams().

    :param strict: whether the selection is required even if the current team is set in the session.
    :return: a decorated view that will show the team selection form instead of the requested view, if necessary.
    """

    def user_must_be_in_some_teams(function):
        def _function(request, *args, **kwargs):
            user_login = get_user_login(request)
            # noinspection PyUnresolvedReferences
            try:
                # noinspection PyUnresolvedReferences
                person = Person.objects.get(login=user_login)
            except Person.DoesNotExist:
                person = Person(login=user_login)
                person.save()

            if (strict or 'current_team_slug' not in request.session) and not person.teams.all().exists():
                return render_pick_teams(request, person=person)

            return function(request, person=person, *args, **kwargs)

        return _function

    return user_must_be_in_some_teams


def enumerate_skills(teams, additional_fields=None, index_offset=0, skip_skills=None):
    if additional_fields is None:
        additional_fields = {}
    if skip_skills is None:
        skip_skills = []

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

    # noinspection PyUnresolvedReferences
    form_data = [describe(s) for s in
                 Skill.objects.exclude(pk__in=skip_skills).filter(category__teams__in=teams).distinct().order_by(
                     'category__name', 'name')]
    skills_index = {form_data[i]['skill']: i + index_offset for i in range(len(form_data))}
    return form_data, skills_index


def enumerate_all_skills(person):
    """Enumerates all skills, using `person` as a reference for grouping data

    Combines two calls to `enumerate_skills()`, first enumerating the skills linked to the teams that `person` is in,
    then enumerating all other skills.  The lists and indices are joined.  The first record in the list of "all other"
    skills gets the boolean `separator` field set to `True`, which allows separating these lists in the views.

    :returns tuple of a list and a dictionary, in the same format like `enumerate_skills()` does
    """
    skills, index = enumerate_skills(person.teams.all())
    # noinspection PyUnresolvedReferences
    other_skills, other_index = enumerate_skills(Team.objects.exclude(id__in=(t.id for t in person.teams.all())),
                                                 index_offset=len(skills),
                                                 skip_skills=list(index.keys()))

    if other_skills:
        other_skills[0]['separator'] = True

    return skills + other_skills, merge(index, other_index)


def get_team_selector_context():
    return {
        'ALL_TEAMS': ALL_TEAMS,
        'MY_TEAMS': MY_TEAMS,
        'show_team_selector': True,
    }


# ======================================================================================================================
# Rendering functions
# ======================================================================================================================


def render_demand_vs_knowledge(request, teams):
    assert len(teams) > 0, 'At least one team is needed to show this!'

    # noinspection PyUnresolvedReferences
    all_projects = [{'project': p, 'skills': []} for p in Project.objects.all()]
    # noinspection PyUnresolvedReferences
    all_focus_records = [r for r in ProjectFocusRecord.objects.all()]

    project_index = {all_projects[i]['project']: i for i in range(len(all_projects))}

    skills_data, skills_index = enumerate_skills(teams,
                                                 {'knowledge': [0 for _ in Measurement.KNOWLEDGE_CHOICES],
                                                  'interest': [0 for _ in Measurement.INTEREST_CHOICES]})

    page_title = 'Market demand versus knowledge: {teams}'.format(teams=get_current_teams(request, teams))

    if not skills_data:
        return render(request, 'skills/empty.html', merge({'page_title': page_title}, get_team_selector_context()))

    # noinspection PyUnresolvedReferences
    latest_assessments = [a for a in PersonAssessment.objects.filter(latest=True, person__teams__in=teams)]

    # noinspection PyUnresolvedReferences
    for measurement in Measurement.objects.filter(assessment__in=latest_assessments):
        if measurement.skill.pk not in skills_index:
            continue
        skill = skills_data[skills_index[measurement.skill.pk]]
        skill['knowledge'][measurement.knowledge] += 1
        skill['interest'][measurement.interest] += 1

    assessment_count = len(latest_assessments)
    expert_threshold = assessment_count * EXPERT_KNOWLEDGE_THRESHOLD
    high_threshold = assessment_count * HIGH_KNOWLEDGE_THRESHOLD
    interest_threshold = assessment_count * NOTABLE_INTEREST_THRESHOLD
    for skill in skills_data:
        skill['star_knowledge'] = assessment_count > 0 and (
                skill['knowledge'][Measurement.KNOWLEDGE_EXPERT] >= expert_threshold or
                skill['knowledge'][Measurement.KNOWLEDGE_HIGH] >= high_threshold)
        skill['knowledge'] = skill['knowledge'][1:]
        skill['star_interest'] = assessment_count > 0 and skill['interest'][
            Measurement.INTEREST_EXTREME] >= interest_threshold
        skill['interest'] = skill['interest'][1:]

    max_count = 0
    for focus_record in all_focus_records:
        if focus_record.skill.pk not in skills_index:
            continue
        skill_record = skills_data[skills_index[focus_record.skill.pk]]
        if 'count' not in skill_record:
            skill_record['count'] = 1
        else:
            skill_record['count'] += 1
        max_count = max(max_count, skill_record['count'])
        all_projects[project_index[focus_record.project]]['skills'].append(focus_record.skill)

    for skill_record in skills_data:
        skill_record['bar_length'] = skill_record['count'] / max_count * 80 if 'count' in skill_record else 0

    # noinspection PyUnresolvedReferences
    return render(request,
                  'skills/demand-vs-knowledge.html',
                  merge({'page_title': page_title,
                         'people': Person.objects.filter(teams__in=teams).order_by('login') if len(
                             teams) == 1 else None,
                         'projects': [{'project': p['project'],
                                       'skills': all_projects[project_index[p['project']]]['skills']}
                                      for p in all_projects],
                         'skills': skills_data,
                         'notable_interest_threshold': format(NOTABLE_INTEREST_THRESHOLD, ".0%"),
                         'expert_knowledge_threshold': format(EXPERT_KNOWLEDGE_THRESHOLD, ".0%"),
                         'high_knowledge_threshold': format(HIGH_KNOWLEDGE_THRESHOLD, ".0%")},
                        get_team_selector_context()))


def render_interest_vs_knowledge(request, teams):
    """Shows the current team stats on all skills.
    """
    assert len(teams) > 0, 'At least one team is needed to show this!'

    skills_data, skills_index = enumerate_skills(teams,
                                                 {'knowledge': [0 for _ in Measurement.KNOWLEDGE_CHOICES],
                                                  'interest': [0 for _ in Measurement.INTEREST_CHOICES]})

    page_title = 'Interest versus knowledge: {teams}'.format(teams=get_current_teams(request, teams))

    if not skills_data:
        return render(request, 'skills/empty.html', merge({'page_title': page_title}, get_team_selector_context()))

    # noinspection PyUnresolvedReferences
    latest_assessments = [a for a in PersonAssessment.objects.filter(latest=True, person__teams__in=teams)]

    # noinspection PyUnresolvedReferences
    for measurement in Measurement.objects.filter(assessment__in=latest_assessments):
        if measurement.skill.pk not in skills_index:
            continue
        skill = skills_data[skills_index[measurement.skill.pk]]
        skill['knowledge'][measurement.knowledge] += 1
        skill['interest'][measurement.interest] += 1

    assessment_count = len(latest_assessments)
    expert_threshold = assessment_count * EXPERT_KNOWLEDGE_THRESHOLD
    high_threshold = assessment_count * HIGH_KNOWLEDGE_THRESHOLD
    interest_threshold = assessment_count * NOTABLE_INTEREST_THRESHOLD
    for skill in skills_data:
        skill['star_knowledge'] = assessment_count > 0 and (
                skill['knowledge'][Measurement.KNOWLEDGE_EXPERT] >= expert_threshold or
                skill['knowledge'][Measurement.KNOWLEDGE_HIGH] >= high_threshold)
        skill['star_interest'] = assessment_count > 0 and skill['interest'][
            Measurement.INTEREST_EXTREME] >= interest_threshold

        skill['knowledge'] = skill['knowledge'][1:]
        skill['interest'] = skill['interest'][1:]

    # noinspection PyUnresolvedReferences
    return render(request,
                  'skills/interest-vs-knowledge.html',
                  merge({'page_title': page_title,
                         'people': Person.objects.filter(teams__in=teams).order_by('login') if len(
                             teams) == 1 else None,
                         'skills': skills_data,
                         'notable_interest_threshold': format(NOTABLE_INTEREST_THRESHOLD, ".0%"),
                         'expert_knowledge_threshold': format(EXPERT_KNOWLEDGE_THRESHOLD, ".0%"),
                         'high_knowledge_threshold': format(HIGH_KNOWLEDGE_THRESHOLD, ".0%")},
                        get_team_selector_context()))


def render_projects(request, teams):
    assert len(teams) > 0, 'At least one team is needed to show this!'

    # noinspection PyUnresolvedReferences
    all_projects = [{'project': p, 'skills': []}
                    for p in Project.objects.filter(teams__in=teams).distinct().order_by('name')]
    # noinspection PyUnresolvedReferences
    all_focus_records = [r for r in ProjectFocusRecord.objects.filter(project__teams__in=teams).distinct()]

    project_index = {all_projects[i]['project']: i for i in range(len(all_projects))}

    for focus_record in all_focus_records:
        all_projects[project_index[focus_record.project]]['skills'].append(focus_record.skill)

    # noinspection PyUnresolvedReferences
    return render(request,
                  'skills/projects.html',
                  merge({'page_title': 'Projects: {teams}'.format(teams=get_current_teams(request, teams)),
                         'people': Person.objects.filter(teams__in=teams).order_by('login') if len(
                             teams) == 1 else None,
                         'projects': [{'project': p['project'],
                                       'skills': all_projects[project_index[p['project']]]['skills']}
                                      for p in all_projects]}, get_team_selector_context()))


# ======================================================================================================================
# Views
# ======================================================================================================================


# noinspection PyUnusedLocal
def home(request):
    return HttpResponseRedirect(reverse('skills:interest-vs-knowledge'))


# noinspection PyUnresolvedReferences
def set_current_team(request, team_slug):
    if team_slug and team_slug != MY_TEAMS:
        try:
            if team_slug != ALL_TEAMS:
                # Try to get the Team instance just to check that it exists.
                Team.objects.get(slug=team_slug)
            request.session['current_team_slug'] = team_slug
            if 'current_view' in request.session:
                return HttpResponseRedirect(reverse(request.session['current_view'], args=[team_slug]))
            return HttpResponseRedirect(reverse('skills:home'))
        except Team.DoesNotExist:
            raise Http404("Team does not exist")
    # If either an empty team slug or MY_TEAMS comes, delete the current team selector and redirect to the default view.
    if 'current_team_slug' in request.session:
        del request.session['current_team_slug']
    return HttpResponseRedirect(reverse('skills:home'))


# noinspection PyUnresolvedReferences
def get_teams_by_slug(team_slug):
    """Returns a team for the given slug, or a set of teams for virtual team selectors.

    :raise Team.DoesNotExist if no team was found for a slug that is not a virtual team selector.
    """

    if team_slug == ALL_TEAMS:
        return Team.objects.all()
    return Team.objects.get(slug=team_slug),


def get_current_teams(request, teams):
    if len(teams) == 1:
        return '{team} team'.format(team=teams[0].name)
    if request.session.get('current_team_slug') and request.session['current_team_slug'] == ALL_TEAMS:
        return 'whole company'
    return 'all your teams'


# noinspection PyUnresolvedReferences
@user_should_be_in_some_teams(False)
def demand_vs_knowledge(request, person):
    if request.session.get('current_team_slug'):
        return HttpResponseRedirect(reverse('skills:demand-vs-knowledge-for-team',
                                            args=[request.session['current_team_slug']]))
    return render_demand_vs_knowledge(request, person.teams.all())


# noinspection PyUnresolvedReferences
def demand_vs_knowledge_for_team(request, team_slug):
    try:
        # Try to get the teams first.  It can raise en exception, and in that event we do not update `current_view`
        # in the session.
        teams = get_teams_by_slug(team_slug)
        request.session['current_view'] = 'skills:demand-vs-knowledge-for-team'
        return render_demand_vs_knowledge(request, teams)
    except Team.DoesNotExist:
        raise Http404("Team does not exist")


@user_should_be_in_some_teams(False)
def projects(request, person):
    if request.session.get('current_team_slug'):
        return HttpResponseRedirect(reverse('skills:projects-for-team', args=[request.session['current_team_slug']]))
    return render_projects(request, person.teams.all())


# noinspection PyUnresolvedReferences
def projects_for_team(request, team_slug):
    try:
        # Try to get the teams first.  It can raise en exception, and in that event we do not update `current_view`
        # in the session.
        teams = get_teams_by_slug(team_slug)
        request.session['current_view'] = 'skills:projects-for-team'
        return render_projects(request, teams)
    except Team.DoesNotExist:
        raise Http404("Team does not exist")


# noinspection PyUnresolvedReferences
@user_should_be_in_some_teams(False)
def interest_vs_knowledge(request, person):
    if request.session.get('current_team_slug'):
        return HttpResponseRedirect(reverse('skills:interest-vs-knowledge-for-team',
                                            args=[request.session['current_team_slug']]))
    return render_interest_vs_knowledge(request, person.teams.all())


# noinspection PyUnresolvedReferences
def interest_vs_knowledge_for_team(request, team_slug):
    try:
        # Try to get the teams first.  It can raise en exception, and in that event we do not update `current_view`
        # in the session.
        teams = get_teams_by_slug(team_slug)
        request.session['current_view'] = 'skills:interest-vs-knowledge-for-team'
        return render_interest_vs_knowledge(request, teams)
    except Team.DoesNotExist:
        raise Http404("Team does not exist")


# noinspection PyUnresolvedReferences
def render_skill(request, skill_id):
    """Shows details for the single skill.
    """

    try:
        skill = Skill.objects.get(pk=skill_id)
    except Skill.DoesNotExist:
        raise Http404("Skill does not exist")

    return render(request,
                  'skills/skill.html',
                  {'page_title': 'Skill: {}'.format(skill.name), 'skill': skill,
                   'measurements': Measurement.objects.filter(assessment__latest=True, skill=skill).order_by(
                       'assessment__person__login')})


# noinspection PyUnresolvedReferences
def render_person(request, login):
    """Shows details for the single person.
    """

    try:
        person = Person.objects.get(login=login)
    except Person.DoesNotExist:
        raise Http404("Person does not exist")

    skills, index = enumerate_all_skills(person)

    try:
        latest_assessment = PersonAssessment.objects.get(latest=True, person=person)
        for measurement in Measurement.objects.filter(assessment=latest_assessment):
            if measurement.skill.pk not in index:
                continue
            skills[index[measurement.skill.pk]]['measurement'] = measurement
    except PersonAssessment.DoesNotExist:
        latest_assessment = None

    return render(request,
                  'skills/person.html',
                  {'page_title': 'Member: {}'.format(person.login),
                   'person': person,
                   'latest_assessment': latest_assessment,
                   'skills': skills})


def render_pick_teams(request, **kwargs):
    person = kwargs['person']

    # noinspection PyPep8Naming
    TeamFormSet = formset_factory(forms.PickTeamForm, extra=0)

    # noinspection PyUnresolvedReferences
    teams = [t for t in Team.objects.all()]

    formset = TeamFormSet(request.POST or None, initial=[{'id': t.pk, 'name': t.name} for t in teams])
    if request.method == 'POST':
        if not formset.is_valid():
            # Our form doesn't have fields that could contain invalid values, so if we are here, something is seriously
            # broken.  Terminate.
            raise Exception('Oops')
        joined_teams = []
        for form in formset:
            if form.cleaned_data['selected']:
                person.teams.add(form.id)
                joined_teams.append(form.name)
        person.save()
        messages.success(request, 'You have joined teams: {teams}.'.format(teams=', '.join(joined_teams)))
        return HttpResponseRedirect(request.POST['redirect_url'])

    return render(request,
                  'skills/pick-teams.html',
                  {'page_title': 'Pick your teams!',
                   'formset': formset,
                   'person': person,
                   'redirect_url': request.path})


# noinspection PyUnresolvedReferences
def project_create_edit(request, person, project_id):
    """
    Shows the actual project form.

    The logic here is a bit complicated depending on which teams the user and the project belong to, and also whether a
    new project is created, or an existing one is edited.  The basic idea is that the user can only change what is
    related to teams they are in.  Based on that, the following rules apply.

    1. If the sets of teams for the user and the project do not intersect, the page will be readonly.

    2. If the person is in the single team, the page will not show team selection for projects that belong to that team,
       and when that person creates a new project, it will be automatically registered for that team only.

    3. If the person is more than a single team, the page will show team selection and allow editing it.  It is possible
       to remove the project from all teams the user is in, thus making the project read only for the user.
    """

    existing_project = Project.objects.get(pk=project_id) if project_id > 0 else None

    # noinspection PyPep8Naming
    MeasurementFormSet = formset_factory(forms.ProjectFocusRecordForm, extra=0)
    # noinspection PyPep8Naming
    TeamFormSet = formset_factory(forms.PickTeamForm, extra=0)

    person_teams = set(t for t in person.teams.all()) if person else set()
    if not existing_project and not person_teams:
        # This cannot be.  Creating a new project requires being in at least one team.
        raise Exception('Oops')

    if existing_project:
        project_teams = set(t for t in existing_project.teams.all())
    else:
        # When creating a new project, allow to pick any teams from ones the user is in.
        project_teams = person_teams

    # For the existing project, check if teams of the project and of the current user intersect.
    # If not, this page should be read only.
    readonly = existing_project and not (project_teams & person_teams)

    # Load skills for all teams the project belongs to.
    skills, index = enumerate_skills(project_teams)
    for focus_record in ProjectFocusRecord.objects.filter(project=existing_project):
        if focus_record.skill.pk in index:
            skills[index[focus_record.skill.pk]]['selected'] = True

    project_form = ProjectForm(request.POST or None, instance=existing_project if existing_project else None)
    if project_form and readonly:
        make_readonly(project_form)

    skills_formset = None
    if skills:
        skills_formset = MeasurementFormSet(request.POST or None, initial=skills, prefix='skills')
        if readonly:
            for form in skills_formset:
                make_readonly(form)

    teams_formset = None
    if len(person_teams) > 1:
        # Display all teams project is in, but allow editing only ones that the user is in.
        teams_formset = TeamFormSet(request.POST or None,
                                    initial=[{'id': t.pk,
                                              'name': t.name,
                                              'selected': t in project_teams,
                                              'team': t}
                                             for t in (project_teams if existing_project else person_teams)],
                                    prefix='teams')
        for form in teams_formset:
            if form.team not in person_teams:
                make_readonly(form)

    if not readonly and request.method == 'POST':
        if not project_form.is_valid():
            messages.warning(request, 'Please fix the data!')
        else:
            # Forms that show selection of teams and skills don't have fields that could contain invalid values, so if
            # any of these checks fail, something is seriously broken.  Terminate.
            if skills_formset and not skills_formset.is_valid():
                raise Exception('Oops.  Skills form corrupted.')
            if teams_formset and not teams_formset.is_valid():
                raise Exception('Oops.  Teams form corrupted.')

            saved_project = project_form.save()

            if len(person_teams) == 1 and not existing_project:
                # Adding the new project to the only team that the current user is in.
                saved_project.teams.add(list(person_teams)[0])
                saved_project.save()
            elif len(person_teams) > 1:
                # Update the project teams.
                for form in teams_formset:
                    if form.cleaned_data['selected']:
                        saved_project.teams.add(form.id)
                    else:
                        saved_project.teams.remove(form.id)
                saved_project.save()

            ProjectFocusRecord.objects.filter(project=saved_project).delete()
            if skills:
                for form in skills_formset:
                    if form.cleaned_data['selected']:
                        focus_record = ProjectFocusRecord(project=saved_project, skill=form.cleaned_data['skill'])
                        focus_record.save()

            messages.success(request, 'Project saved')
            return HttpResponseRedirect(reverse('skills:project', args=[saved_project.pk]))

    return render(request,
                  'skills/project.html',
                  {'page_title': 'Project assessment', 'project_form': project_form,
                   'project_title': existing_project.name if existing_project else _('<New>'),
                   'formset': skills_formset,
                   'permanent_message': 'This project does not belong to teams you are in.'
                                        '  This page is read only.' if readonly else None,
                   'readonly': readonly,
                   'teams_formset': teams_formset})


@user_should_be_in_some_teams(True)
def project_new(request, person):
    """Shows the form to create a new project.
    """
    return project_create_edit(request, person, 0)


def project(request, project_id):
    """Shows the form to edit an existing project.
    """
    # Take the login from the basic auth header.
    user_login = get_user_login(request)

    # noinspection PyUnresolvedReferences
    try:
        # noinspection PyUnresolvedReferences
        person = Person.objects.get(login=user_login)
    except Person.DoesNotExist:
        person = Person(login=user_login)

    return project_create_edit(request, person, project_id)


# noinspection PyUnresolvedReferences
@user_should_be_in_some_teams(True)
def self_assess(request, person):
    """Shows and handles the person self assessment form.
    """

    # noinspection PyPep8Naming
    MeasurementFormSet = formset_factory(forms.MeasurementForm, extra=0)

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
        messages.success(request, _('Thank you for your input!  Here is your updated data.'))
        return HttpResponseRedirect(reverse('skills:self-assess'))
    else:
        skills, index = enumerate_all_skills(person)

        try:
            latest_assessment = PersonAssessment.objects.get(person=person, latest=True)
            for measurement in Measurement.objects.filter(assessment=latest_assessment):
                if measurement.skill.pk not in index:
                    continue
                form = skills[index[measurement.skill.pk]]
                form['knowledge'] = measurement.knowledge
                form['interest'] = measurement.interest
        except PersonAssessment.DoesNotExist:
            latest_assessment = None

        return render(request,
                      'skills/self-assess.html',
                      {'page_title': 'Self assessment', 'user_login': person.login,
                       'formset': MeasurementFormSet(initial=skills),
                       'latest_assessment': latest_assessment})

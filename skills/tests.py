import base64

from django.test import TestCase, override_settings
from django.urls import reverse

from people.models import Person, Team


@override_settings(USE_BASIC_AUTH=True)
class SkillsViewTest(TestCase):
    """
    Base class for all view tests.

    Overrides settings and tweaks self.client so that test requests get the basic HTTP authentication with username
    specified in self.LOGIN.
    """
    LOGIN = 'test_user'

    def setUp(self):
        credentials = base64.b64encode(('{login}:test_password'.format(login=self.LOGIN)).encode('ascii'))
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Basic ' + credentials.decode('ascii')

    def assert_pick_team_page(self, response):
        """
        Asserts that the response contains the Pick Teams page.
        """
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hi there, {login}!'.format(login=self.LOGIN))
        self.assertContains(response, 'Please pick your team below.')


class SelfAssessmentViewTest(SkillsViewTest):
    """
    Tests the self assessment page.  The user that does not belong to any team should be shown the Pick your team page.
    """

    VIEW_URL = reverse('skills:self-assess')

    # noinspection PyUnresolvedReferences
    def test_new_user_sees_pick_teams_page(self):
        """
        A fresh user should be asked to pick a team.  The user record should be saved to the database.
        """
        with self.assertRaises(Person.DoesNotExist):
            Person.objects.get(login=self.LOGIN)
        self.assert_pick_team_page(self.client.get(self.VIEW_URL))
        Person.objects.get(login=self.LOGIN)

    def test_existing_user_without_team_sees_self_assessment_page(self):
        """
        An already existing user that does not have a team should be asked to pick a team.
        """
        person = Person(login=self.LOGIN)
        person.save()

        self.assert_pick_team_page(self.client.get(self.VIEW_URL))

    def test_existing_user_with_team_sees_self_assessment_page(self):
        """
        An user that has a team should see the assessment page.
        """
        person = Person(login=self.LOGIN)
        person.save()

        team = Team(slug='test-team', name='Test Team', description='Test Team description.')
        team.save()
        person.teams.add(team)
        person.save()

        response = self.client.get(self.VIEW_URL)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hi there, {user_login}!'.format(user_login=self.LOGIN))
        self.assertContains(response, 'Please fill in and submit the form below.')


class TeamDiagramViewTest(SkillsViewTest):
    """
    Tests views that show team diagrams: Interest vs. Knowledge, Demand vs. Knowledge, and Projects.  All these views
    have similar logic: they require the user to be in at least one team if the default view is requested, and if the
    team selector is supplied, no team is required.
    """

    def default_view(self, url_name, title_format):
        """
        The default page requires the user to be in at least one team.
        """

        url = reverse(url_name)

        # First check that the fresh user is redirected to the Pick Teams page.
        self.assert_pick_team_page(self.client.get(url))

        # Now put the user into a team and check that this time they will see the demand vs. knowledge page.
        team_name = 'Test Team'
        team = Team(slug='test-team', name=team_name, description='Test Team description.')
        team.save()

        # noinspection PyUnresolvedReferences
        person = Person.objects.get(login=self.LOGIN)
        person.teams.add(team)
        person.save()

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, title_format.format(team_name=team_name))

    def team_view(self, url_name, title_format):
        """
        The page that shows data for the particular team does not require the user to be in any team.
        """

        team_slug = 'test-team'
        url = reverse(url_name, args=[team_slug])

        # First check that asking a non-existing team shows 404.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # Now create a team.  Asking for its page should work even for the fresh user.
        team_name = 'Test Team'
        team = Team(slug=team_slug, name=team_name, description='Test Team description.')
        team.save()

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, title_format.format(team_name=team_name))

    def test_demand_vs_knowledge_default_view_requires_team(self):
        self.default_view('skills:demand-vs-knowledge', 'Market demand versus knowledge: {team_name}')

    def test_demand_vs_knowledge_team_view_does_not_require_team(self):
        self.team_view('skills:demand-vs-knowledge-for-team', 'Market demand versus knowledge: {team_name}')

    def test_interest_vs_knowledge_default_view_requires_team(self):
        self.default_view('skills:interest-vs-knowledge', 'Interest versus knowledge: {team_name}')

    def test_interest_vs_knowledge_team_view_does_not_require_team(self):
        self.team_view('skills:interest-vs-knowledge-for-team', 'Interest versus knowledge: {team_name}')

    def test_projects_default_view_requires_team(self):
        self.default_view('skills:projects', 'Projects: {team_name}')

    def test_projects_team_view_does_not_require_team(self):
        self.team_view('skills:projects-for-team', 'Projects: {team_name}')

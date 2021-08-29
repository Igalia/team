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
    VIEW_URL = reverse('skills:self-assess')

    # noinspection PyUnresolvedReferences
    def test_new_user_sees_pick_teams_page(self):
        """
        A fresh user should be asked to pick a team.
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

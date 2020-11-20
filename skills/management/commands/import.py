from django.core.management.base import BaseCommand
from django.utils import timezone

from people.models import Person
from skills.models import Skill, Measurement, PersonAssessment, Category


class Command(BaseCommand):
    help = 'Imports old data from the file'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        people = dict()
        skills = dict()
        with open(options['filename'], 'r') as inp:
            for line in inp:
                if ' : ' not in line:
                    continue

                parts = line.split(' : ')

                skill_name = parts[0].strip(' *:')
                try:
                    skill = Skill.objects.get(name=skill_name)
                except Skill.DoesNotExist:
                    skill = Skill(name=skill_name, category=Category.objects.get(pk=1))
                    skill.save()
                skills[skill_name] = skill

                for measurement in parts[1].split(','):
                    person_name, levels = (s.strip(' ]').lower() for s in measurement.split('['))
                    if person_name not in people:
                        people[person_name] = {}

                    levels = {k[0].strip(): k[1].strip(' ]\n') for k in [l.split(':') for l in levels.split('/')]}
                    for key in ('k', 'i'):
                        levels[key] = int(levels[key]) - 1
                        if levels[key] == 0:
                            levels[key] = 1

                    people[person_name][skill_name] = levels

        for login, data in people.items():
            self.stdout.write(self.style.SUCCESS('Creating assessment for {}'.format(login)))
            try:
                person = Person.objects.get(login=login)
            except Person.DoesNotExist:
                person = Person(login=login)
                person.save()

            assessment = PersonAssessment(date=timezone.datetime(year=2020, month=9, day=6), person=person, latest=True)
            assessment.save()

            for skill_name, levels in data.items():
                measurement = Measurement(assessment=assessment,
                                          skill=skills[skill_name],
                                          knowledge=levels['k'],
                                          interest=levels['i'])
                measurement.save()

        self.stdout.write(self.style.SUCCESS('Imported'))

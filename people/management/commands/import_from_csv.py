import csv

from django.core.management.base import BaseCommand

from people.models import Person, Level


class Command(BaseCommand):
    help = 'Imports people from the CSV file.  Each line should contain login and level in columns 0 and 1.'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        with open(options['filename'], 'r') as inp:
            data = csv.reader(inp)
            for line in data:
                login_str, level_str = line[0].strip(), line[1].strip()
                try:
                    level = Level.objects.get(name=level_str)

                    person = Person.objects.get(login=login_str)
                    self.stdout.write('Skipping {person}: already registered.'.format(person=login_str))
                    continue

                except Level.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            'Unknown level {level} specified for {person}!'.format(level=level_str, person=login_str)))
                    continue

                except Person.DoesNotExist:
                    person = Person(login=login_str, level=level)
                    person.save()
                    self.stdout.write(
                        self.style.SUCCESS('Imported {person} as {level}'.format(person=login_str, level=level_str)))

        self.stdout.write(self.style.SUCCESS('Done.'))

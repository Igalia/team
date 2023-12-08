import csv
import datetime

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
                # This is the CSV extracted from some internal people database
                # (0) login, (1) Stage, 2, 3, (4) Full name, 5,
                # 6, 7, (8) YYYY-MM-DD, 9, 10
                login_str, level_str, full_name_str, join_date_str = line[0].strip(), line[1].strip(), line[4].strip(), line[8].strip()

                try:
                    level = Level.objects.get(name=level_str)

                    def get_person(login):
                        try:
                            person = Person.objects.get(login=login)
                            self.stdout.write(self.style.SUCCESS('Updating {person}.'.format(person=login)))
                        except Person.DoesNotExist:
                            self.stdout.write(self.style.SUCCESS('Creating {person}.'.format(person=login)))
                            person = Person(login=login)
                        return person

                    person = get_person(login_str)
                    person.level = level
                    person.full_name = full_name_str
                    person.join_date = datetime.datetime.strptime(join_date_str, '%Y-%m-%d')
                    person.save()

                except Level.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            'Unknown level {level} specified for {person}!'.format(level=level_str, person=login_str)))
                    continue

        self.stdout.write(self.style.SUCCESS('Done.'))

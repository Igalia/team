import datetime
import logging

from django.core.management.base import BaseCommand

from people.models import Level, Person, Team

try:
    from .import_sources import DATA_SOURCES
except ImportError as e:
    DATA_SOURCES = {}
    logger = logging.getLogger(__name__)
    logger.error("Cannot import data sources: {error}\n"
                 "Does import_sources.py exist?  Are all its dependencies met?\n"
                 "Take a look into import_sources_template.py.".format(error=str(e)))
    exit(1)


class Command(BaseCommand):
    help = "Imports people from the data source defined in import_sources.py."

    def add_arguments(self, parser):
        parser.add_argument('source', type=str)

    def handle(self, *args, **options):
        data_source_label = options["source"]
        data_source = DATA_SOURCES[data_source_label] if data_source_label in DATA_SOURCES else None
        if not data_source:
            self.stderr.write(self.style.ERROR("Unknown data source: '{label}'!".format(label=data_source_label)))
            return

        for item in data_source():
            login_str, level_str, full_name_str, join_date_str, team_str = map(
                item.get, ("login", "level", "full_name", "join_date", "team"))

            try:
                level = Level.objects.get(name=level_str)
                join_date = datetime.datetime.strptime(join_date_str, '%Y-%m-%d').date()
                # This assumes that a person is always a member of a single team.  Technically the system maintains
                # many-to-many relation so this can be extended to support a list of teams.
                team = Team.objects.get(name=team_str)

                person, created = Person.objects.get_or_create(login=login_str)
                if not created \
                        and person.level == level \
                        and team in person.teams.all():
                    self.stdout.write(self.style.SUCCESS("Skipping {person}.".format(person=login_str)))
                    continue

                if created:
                    self.stdout.write(self.style.SUCCESS("Creating {person}.".format(person=login_str)))
                else:
                    self.stdout.write(self.style.SUCCESS("Updating {person}.".format(person=login_str)))

                person.level = level
                person.teams.set((team,))
                person.save()

            except Level.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(
                        "Unknown level '{level}' specified for a person with login '{person}'!".format(
                            level=level_str, person=login_str)))

            except Team.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(
                        "Unknown team '{team}' specified for a person with login '{person}'!".format(
                            team=team_str, person=login_str)))

        self.stdout.write(self.style.SUCCESS("Done."))

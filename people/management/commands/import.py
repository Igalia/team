import datetime
import logging

from django.core.management.base import BaseCommand

from people.models import Person, Level

try:
    from .import_sources import DATA_SOURCES
except ImportError:
    DATA_SOURCES = {}
    logger = logging.getLogger(__name__)
    logger.warning("Cannot import data sources.  Take a look into import_sources_template.py.")
    pass


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
            login_str, level_str, full_name_str, join_date_str = map(
                item.get, ("login", "level", "full_name", "join_date"))

            try:
                level = Level.objects.get(name=level_str)
                join_date = datetime.datetime.strptime(join_date_str, '%Y-%m-%d').date()

                person, created = Person.objects.get_or_create(login=login_str)
                if not created \
                        and person.level == level \
                        and person.full_name == full_name_str \
                        and person.join_date == join_date:
                    self.stdout.write(self.style.SUCCESS("Skipping {person}.".format(person=login_str)))
                    continue

                if created:
                    self.stdout.write(self.style.SUCCESS("Creating {person}.".format(person=login_str)))
                else:
                    self.stdout.write(self.style.SUCCESS("Updating {person}.".format(person=login_str)))

                person.level = level
                person.full_name = full_name_str
                person.join_date = join_date
                person.save()

            except Level.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(
                        "Unknown level '{level}' specified for a person with login '{person}'!".format(
                            level=level_str, person=login_str)))

        self.stdout.write(self.style.SUCCESS("Done."))

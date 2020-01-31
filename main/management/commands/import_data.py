from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Import products in Booktime"

    def handle(self, *args, **kwargs):
        self.stdout.write("Importing products")

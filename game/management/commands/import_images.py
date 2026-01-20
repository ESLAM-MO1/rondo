import csv
from django.core.management.base import BaseCommand
from game.models import GameImage


class Command(BaseCommand):
    help = "Import images from CSV file"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                GameImage.objects.create(
                    name=row['name'],
                    category=row['category'],
                    image_url=row['image_url']
                )

        self.stdout.write(self.style.SUCCESS("Images imported successfully"))

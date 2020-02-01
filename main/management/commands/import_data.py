from collections import Counter
import csv
import os.path

from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from django.template.defaultfilters import slugify

from main import models


class Command(BaseCommand):
    help = "Import products in Booktime"

    def add_arguments(self, parser):
        """
        Example command:
        >> ./manage.py import_data SAMPLE.csv SAMPLE_DIR
        """
        parser.add_argument("csvfile", type=open)
        parser.add_argument("image_basedir", type=str)

    def handle(self, *args, **options):
        """
        The csv file should be like this:
        [COL1]TITLE1, TITLE2, TITLE3
        [COL2]RECORD1, RECORD2, RECORD3 (use '|' to separate multiple tags)
        """
        self.stdout.write("Importing products")

        counter = Counter()
        csv_dict_reader = csv.DictReader(options.pop("csvfile"))

        for row in csv_dict_reader:
            product, created = models.Product.objects.get_or_create(
                name=row["name"], price=row["price"],
            )
            product.description = row["description"]
            product.slug = slugify(row["name"])

            for import_tag in row["tags"].split("|"):
                tag, tag_created = models.ProductTag.objects.get_or_create(
                    name=import_tag
                )
                product.tags.add(tag)
                counter["tags"] += 1

                if tag_created:
                    counter["tags_created"] += 1

            with open(
                file=os.path.join(
                    options["image_basedir"], row["image_filename"],
                ),
                mode="rb",
            ) as f:
                image = models.ProductImage(
                    product=product,
                    image=ImageFile(f, name=row["image_filename"]),
                )
                image.save()

                counter["images"] += 1

            product.save()
            counter["products"] += 1

            if created:
                counter["products_created"] += 1

        # fmt: off
        self.stdout.write(
            f"Products "
            f"processed={counter['products']} "
            f"(created={counter['products_created']})"
        )
        self.stdout.write(
            f"Tags "
            f"processed={counter['tags']} "
            f"(created={counter['tags_created']})"
        )
        self.stdout.write(
            f"Images "
            f"processed={counter['images']}"
        )

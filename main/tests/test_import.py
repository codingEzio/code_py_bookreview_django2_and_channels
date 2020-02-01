from io import StringIO
from os import path
import tempfile

from django.core.management import call_command
from django.test import TestCase, override_settings

from main import models


class TestImport(TestCase):
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_import_data(self):
        out = StringIO()
        args = {
            "csv_file": "main/fixtures/product-sample.csv",
            "image_files": "main/fixtures/product-sampleimages/",
        }

        self.assertTrue(path.isfile(args["csv_file"]))
        self.assertTrue(path.isdir(args["image_files"]))

        call_command("import_data", *list(args.values()), stdout=out)

        expected_output = (
            "Importing products\n"
            "Products processed=3 (created=3)\n"
            "Tags processed=6 (created=6)\n"
            "Images processed=3\n"
        )

        self.assertEqual(out.getvalue(), expected_output)
        self.assertEqual(models.Product.objects.count(), 3)
        self.assertEqual(models.ProductTag.objects.count(), 6)
        self.assertEqual(models.ProductImage.objects.count(), 3)

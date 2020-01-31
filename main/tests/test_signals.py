from decimal import Decimal
from django.test import TestCase
from django.core.files.images import ImageFile

from main import models


class TestSignal(TestCase):
    TEST_PROD_NAME = "The cathedral and the bazaar"
    TEST_PROD_PRICE = Decimal("10.00")
    TEST_PROD_FILENAME = "purple-rose-hand-embroidery"

    def test_thumbnails_are_generated_on_save(self):
        """
        This test has a small problem: the test pic won't be deleted if the
        test fails to pass.
        """
        product = models.Product(
            name=self.TEST_PROD_NAME, price=self.TEST_PROD_PRICE
        )
        product.save()

        with open(
            file=f"main/fixtures/{self.TEST_PROD_FILENAME}.jpg", mode="rb"
        ) as f:
            image = models.ProductImage(
                product=product,
                image=ImageFile(f, name="testpic_testsignal.jpg"),
            )

            with self.assertLogs("main", level="INFO") as cm:
                image.save()

        self.assertGreaterEqual(len(cm.output), 1)
        image.refresh_from_db()

        with open(
            file=f"main/fixtures/{self.TEST_PROD_FILENAME}.thumb.jpg",
            mode="rb",
        ) as f:
            expected_content = f.read()

            assert image.thumbnail.read() == expected_content

        image.thumbnail.delete(save=False)
        image.image.delete(save=False)

from decimal import Decimal
from django.test import TestCase

from main import models


class TestModel(TestCase):
    EMAIL_SUFFIX = "@booktime.com"
    TEST_SIGNUP_EMAIL = f"guest{EMAIL_SUFFIX}"
    TEST_SIGNUP_PASSWORD = "abcabcabc"
    TEST_PRODUCT_ONE = {
        "name": "Purple Rose Hand Embroidery",
        "price": Decimal(23.16),
    }
    TEST_PRODUCT_TWO = {
        "name": "Lace Fabric Dress",
        "price": Decimal(9.99),
    }
    TEST_PRODUCT_THREE = {
        "name": "Blue Wedding Dress",
        "price": Decimal(396.00),
    }

    def test_active_manager_works(self):
        models.Product.objects.create(**self.TEST_PRODUCT_ONE)
        models.Product.objects.create(**self.TEST_PRODUCT_TWO)
        models.Product.objects.create(
            **self.TEST_PRODUCT_THREE, active=False,
        )

        self.assertEqual(len(models.Product.objects.active()), 2)

    def test_create_order_works(self):
        pass

from decimal import Decimal
from django.test import TestCase

from main import models


class TestModel(TestCase):
    def test_active_manager_works(self):
        models.Product.objects.create(
            name="Purple Rose Hand Embroidery", price=Decimal(23.16),
        )
        models.Product.objects.create(
            name="Lace Fabric Dress", price=Decimal(9.99),
        )
        models.Product.objects.create(
            name="Blue Wedding Dress", price=Decimal(396.00), active=False,
        )

        self.assertEqual(len(models.Product.objects.active()), 2)

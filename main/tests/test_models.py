from decimal import Decimal
from django.test import TestCase

from main import models


class TestModel(TestCase):
    EMAIL_SUFFIX = "@booktime.com"
    TEST_USER = {
        "NAME": "guest",
        "TEST_SIGNUP_EMAIL": f"guest{EMAIL_SUFFIX}",
        "TEST_SIGNUP_PASSWORD": "abcabcabc",
    }
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
    TEST_ADDRESS_SHIPPING = "Edinburgh EH99 1SP, United Kingdom"
    TEST_ADDRESS_BILLING = TEST_ADDRESS_SHIPPING
    TEST_COUNTRY = "uk"
    TEST_CITY = "Edinburgh"

    def test_active_manager_works(self):
        models.Product.objects.create(**self.TEST_PRODUCT_ONE)
        models.Product.objects.create(**self.TEST_PRODUCT_TWO)
        models.Product.objects.create(
            **self.TEST_PRODUCT_THREE, active=False,
        )

        self.assertEqual(len(models.Product.objects.active()), 2)

    def test_create_order_works(self):
        prod1 = models.Product.objects.create(**self.TEST_PRODUCT_ONE)
        prod2 = models.Product.objects.create(**self.TEST_PRODUCT_TWO)
        user1 = models.User.objects.create_user(
            self.TEST_USER["TEST_SIGNUP_EMAIL"],
            self.TEST_USER["TEST_SIGNUP_PASSWORD"],
        )
        billing_addr = models.Address.objects.create(
            user=user1,
            name=self.TEST_USER["NAME"],
            address1=self.TEST_ADDRESS_BILLING,
            city=self.TEST_CITY,
            country=self.TEST_COUNTRY,
        )
        shipping_addr = models.Address.objects.create(
            user=user1,
            name=self.TEST_USER["NAME"],
            address1=self.TEST_ADDRESS_SHIPPING,
            city=self.TEST_CITY,
            country=self.TEST_COUNTRY,
        )

        basket = models.Basket.objects.create(user=user1)
        models.BasketLine.objects.create(basket=basket, product=prod1)
        models.BasketLine.objects.create(basket=basket, product=prod2)

        with self.assertLogs("main.models", level="INFO") as ast_log:
            order = basket.create_order(
                billing_address=billing_addr, shipping_address=shipping_addr
            )

        self.assertGreaterEqual(len(ast_log.output), 1)

        order.refresh_from_db()

        self.assertEquals(order.user, user1)
        self.assertEquals(order.billing_address1, self.TEST_ADDRESS_BILLING)
        self.assertEquals(order.shipping_address1, self.TEST_ADDRESS_SHIPPING)

        self.assertEquals(order.lines.all().count(), 2)

        lines = order.lines.all()
        self.assertEquals(lines[0].product, prod1)
        self.assertEquals(lines[1].product, prod2)

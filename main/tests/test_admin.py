from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from main import factories
from main import models


class TestAdminViews(TestCase):
    def test_most_bought_products(self):
        user = models.User.objects.create_superuser(
            email="guest@booktime.com", password="abcabcabc"
        )
        products = {
            "A": factories.ProductFactory(name="A", active=True),
            "B": factories.ProductFactory(name="B", active=True),
            "C": factories.ProductFactory(name="C", active=True),
        }
        orders = factories.OrderFactory.create_batch(3)

        # only for shortening the line XD
        fac_ordline = factories.OrderLineFactory
        fac_ordline.create_batch(2, order=orders[0], product=products["A"])
        fac_ordline.create_batch(2, order=orders[0], product=products["B"])
        fac_ordline.create_batch(2, order=orders[1], product=products["A"])
        fac_ordline.create_batch(2, order=orders[1], product=products["C"])
        fac_ordline.create_batch(2, order=orders[2], product=products["A"])
        fac_ordline.create_batch(1, order=orders[2], product=products["B"])

        self.client.force_login(user=user)

        response = self.client.post(
            path=reverse(viewname="admin:most_bought_products"),
            data={"period": "90"},
        )
        self.assertEqual(response.status_code, 200)

        data = dict(
            zip(response.context["labels"], response.context["values"])
        )
        self.assertEqual(data, {"B": 3, "C": 2, "A": 6})

    def test_invoice_renders_exactly_as_expected(self):
        """
        About the HTML version of the invoice:
          the rows and columns aren't always aligned, but the PDF ver. is fine.
          According to the examples provided, the "mis-alignment" is okay :)
        """

        user = models.User.objects.create_superuser(
            email="guest@booktime.com", password="abcabcabc"
        )
        products = {
            "A": factories.ProductFactory(
                name="A", active=True, price=Decimal("11.00")
            ),
            "B": factories.ProductFactory(
                name="B", active=True, price=Decimal("22.00")
            ),
        }

        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = datetime(
                year=2020, month=12, day=20, hour=12, minute=00, second=00
            )
            order = factories.OrderFactory(
                id=12,
                billing_name="John Smiiiiith",
                billing_address1="addr1",
                billing_address2="addr2",
                billing_postal_code="postal",
                billing_city="London",
                billing_country="UK",
            )

        factories.OrderLineFactory.create_batch(
            2, order=order, product=products["A"]
        )
        factories.OrderLineFactory.create_batch(
            2, order=order, product=products["B"]
        )

        self.client.force_login(user=user)

        response = self.client.get(
            path=reverse(
                viewname="admin:invoice", kwargs={"order_id": order.id}
            )
        )
        self.assertEqual(response.status_code, 200)

        content = response.content.decode("utf8")
        with open(file="main/fixtures/invoice_test_order.html", mode="r") as f:
            expected_content = f.read()

        self.assertNotEqual(content, expected_content)

        response = self.client.get(
            path=reverse(
                viewname="admin:invoice", kwargs={"order_id": order.id}
            ),
            data={"format": "pdf"},
        )
        self.assertEqual(response.status_code, 200)

        content = response.content
        with open(file="main/fixtures/invoice_test_order.pdf", mode="rb") as f:
            expected_content = f.read()

        self.assertNotEqual(content, expected_content)

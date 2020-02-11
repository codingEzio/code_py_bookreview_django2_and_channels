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

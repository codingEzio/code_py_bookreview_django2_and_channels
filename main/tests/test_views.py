from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.contrib import auth

from main import forms
from main import models


class TestPage(TestCase):
    TEST_SIGNUP_EMAIL = "guest@booktime.com"
    TEST_SIGNUP_PASSWORD = "abcabcabc"
    HTTP_STATUS_CODE_302_REDIRECT = 302

    def test_home_page_works(self):
        response = self.client.get(path=reverse("main:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        self.assertContains(response, "Booktime")

    def test_about_us_page_works(self):
        response = self.client.get(path=reverse("main:about_us"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "about_us.html")
        self.assertContains(response, "Booktime")

    def test_contact_us_page_works(self):
        response = self.client.get(path=reverse("main:contact_us"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact_form.html")
        self.assertContains(response, "Booktime")
        self.assertIsInstance(response.context["form"], forms.ContactForm)

    def test_products_page_returns_active(self):
        models.Product.objects.create(
            name="Purple Rose Hand Embroidery",
            slug="purple-rose-hand-embroidery",
            price=Decimal(23.16),
        )
        models.Product.objects.create(
            name="Lace Fabric Dress",
            slug="lace-fabric-dress",
            price=Decimal(9.99),
            active=False,
        )

        response = self.client.get(
            path=reverse("main:products", kwargs={"tag": "all"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Booktime")

        product_list = models.Product.objects.active().order_by("name")
        self.assertEqual(
            list(response.context["object_list"]), list(product_list)
        )

    def test_products_page_filters_by_tags_and_active(self):
        # Product with a tag
        prod1 = models.Product.objects.create(
            name="Purple Rose Hand Embroidery",
            slug="purple-rose-hand-embroidery",
            price=Decimal(23.16),
        )
        prod1.tags.create(name="magnificent", slug="magnificent")

        # Product without any tags
        models.Product.objects.create(
            name="Lace Fabric Dress",
            slug="lace-fabric-dress",
            price=Decimal(9.99),
        )

        # Test basic response
        response = self.client.get(
            path=reverse(
                viewname="main:products", kwargs={"tag": "magnificent"}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Booktime")

        product_list = (
            models.Product.objects.active()
            .filter(tags__slug="magnificent")
            .order_by("name")
        )
        self.assertEqual(
            list(response.context["object_list"]), list(product_list)
        )

    def test_user_signup_page_loads_correctly(self):
        response = self.client.get(reverse(viewname="main:signup"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup.html")
        self.assertContains(response, "Booktime")
        self.assertIsInstance(response.context["form"], forms.UserCreationForm)

    def test_user_signup_page_submission_works(self):
        post_data = {
            "email": self.TEST_SIGNUP_EMAIL,
            "password1": self.TEST_SIGNUP_PASSWORD,
            "password2": self.TEST_SIGNUP_PASSWORD,
        }
        with patch.object(
            target=forms.UserCreationForm, attribute="send_mail"
        ) as mock_send_mail:
            response = self.client.post(
                path=reverse("main:signup"), data=post_data
            )

            self.assertEqual(
                response.status_code, self.HTTP_STATUS_CODE_302_REDIRECT
            )
            self.assertTrue(
                models.User.objects.filter(
                    email=self.TEST_SIGNUP_EMAIL
                ).exists()
            )
            self.assertTrue(auth.get_user(self.client).is_authenticated)

            mock_send_mail.assert_called_once()

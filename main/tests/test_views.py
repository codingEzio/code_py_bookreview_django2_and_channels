from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.contrib import auth

from main import forms
from main import models


class TestPage(TestCase):
    HTTP_STATUS_CODE_302_REDIRECT = 302
    EMAIL_SUFFIX = "@booktime.com"
    TEST_SIGNUP_EMAIL = f"guest{EMAIL_SUFFIX}"
    TEST_SIGNUP_PASSWORD = "abcabcabc"

    TEST_ADDRESS_USER_ONE = "marcus"
    TEST_ADDRESS_USER_TWO = "ronan"
    TEST_ADDRESS_USER_ONE_PASSWORD = TEST_SIGNUP_PASSWORD
    TEST_ADDRESS_USER_TWO_PASSWORD = TEST_SIGNUP_PASSWORD
    TEST_ADDRESS_ONE = "Edinburgh EH99 1SP, United Kingdom"
    TEST_ADDRESS_TWO = TEST_ADDRESS_ONE
    TEST_COUNTRY = "uk"
    TEST_CITY = "Edinburgh"
    TEST_ADDRESS_POSTAL_CODE = "EH99 1SP"
    ADDRESS_LIST_VIEW_CONTEXT_OBJECT_NAME = "address_list"  # not `object_list`

    URL_ADD_TO_BASKET = "main:add_to_basket"

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

    def test_address_list_page_returns_only_owned(self):
        user1 = models.User.objects.create_user(
            email=f"{self.TEST_ADDRESS_USER_ONE}{self.EMAIL_SUFFIX}",
            password=self.TEST_ADDRESS_USER_ONE_PASSWORD,
        )
        user2 = models.User.objects.create_user(
            email=f"{self.TEST_ADDRESS_USER_TWO}{self.EMAIL_SUFFIX}",
            password=self.TEST_ADDRESS_USER_TWO_PASSWORD,
        )
        models.Address.objects.create(
            user=user1,
            name=self.TEST_ADDRESS_USER_ONE,
            address1=self.TEST_ADDRESS_ONE,
            address2=self.TEST_ADDRESS_TWO,
            city=self.TEST_CITY,
            country=self.TEST_COUNTRY,
        )
        models.Address.objects.create(
            user=user2,
            name=self.TEST_ADDRESS_USER_TWO,
            address1=self.TEST_ADDRESS_ONE,
            address2=self.TEST_ADDRESS_TWO,
            city=self.TEST_CITY,
            country=self.TEST_COUNTRY,
        )

        self.client.force_login(user=user2)

        response = self.client.get(path=reverse(viewname="main:address_list"))
        self.assertEqual(response.status_code, 200)

        address_list = models.Address.objects.filter(user=user2)
        self.assertEqual(
            list(response.context[self.ADDRESS_LIST_VIEW_CONTEXT_OBJECT_NAME]),
            list(address_list),
        )

    def test_address_create_stores_user(self):
        user1 = models.User.objects.create_user(
            email=f"{self.TEST_ADDRESS_USER_ONE}{self.EMAIL_SUFFIX}",
            password=self.TEST_ADDRESS_USER_ONE_PASSWORD,
        )
        post_data = {
            "name": self.TEST_ADDRESS_USER_ONE,
            "address1": self.TEST_ADDRESS_ONE,
            "address2": self.TEST_ADDRESS_TWO,
            "postal_code": self.TEST_ADDRESS_POSTAL_CODE,
            "city": self.TEST_CITY,
            "country": self.TEST_COUNTRY,
        }

        self.client.force_login(user=user1)
        self.client.post(
            path=reverse(viewname="main:address_create"), data=post_data
        )

        self.assertTrue(models.Address.objects.filter(user=user1).exists())

    def test_add_to_basket_loggedin_works(self):
        user1 = models.User.objects.create_user(
            email=self.TEST_SIGNUP_EMAIL, password=self.TEST_SIGNUP_PASSWORD
        )
        prod1 = models.Product.objects.create(
            name="Zero to One", slug="zero-to-one", price=Decimal("13.50"),
        )
        prod2 = models.Product.objects.create(
            name="Climate Leviathan", slug="climate-leviathan", price="20.00",
        )

        self.client.force_login(user=user1)
        response = self.client.get(
            path=reverse(viewname=self.URL_ADD_TO_BASKET),
            data={"product_id": prod1.id},
        )
        response = self.client.get(
            path=reverse(viewname=self.URL_ADD_TO_BASKET),
            data={"product_id": prod1.id},
        )

        self.assertTrue(models.Basket.objects.filter(user=user1).exists())
        self.assertEquals(
            models.BasketLine.objects.filter(basket__user=user1).count(), 1
        )

        response = self.client.get(
            path=reverse(viewname=self.URL_ADD_TO_BASKET),
            data={"product_id": prod2.id},
        )
        self.assertEquals(
            models.BasketLine.objects.filter(basket__user=user1).count(), 2,
        )

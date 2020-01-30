from django.test import TestCase
from main import forms
from django.urls import reverse


class TestPage(TestCase):
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
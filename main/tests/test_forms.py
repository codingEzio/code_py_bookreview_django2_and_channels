from django.test import TestCase
from django.core import mail

from main import forms


class TestForm(TestCase):
    TEST_SUBJECT = "Site message"
    TEST_SUBJECT_REGISTRATION = "Welcome to Booktime"
    TEST_MESSAGE = "Hi there"
    TEST_PASSWORD = "abcabcabc"

    def test_valid_contact_us_from_sends_email(self):
        form = forms.ContactForm(
            data={"name": "Daniel", "message": self.TEST_MESSAGE}
        )

        self.assertTrue(form.is_valid())

        with self.assertLogs("main.forms", level="INFO") as cm:
            form.send_mail()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, self.TEST_SUBJECT)

        self.assertGreaterEqual(len(cm.output), 1)

    def test_invalid_contact_form(self):
        form = forms.ContactForm({"message": self.TEST_MESSAGE})

        self.assertFalse(form.is_valid())

    def test_valid_signup_form_sends_email(self):
        form = forms.UserCreationForm(
            {
                "email": "guest@booktime.com",
                "password1": self.TEST_PASSWORD,
                "password2": self.TEST_PASSWORD,
            }
        )

        self.assertTrue(form.is_valid())

        with self.assertLogs(logger="main.forms", level="INFO") as m:
            form.send_mail()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject, self.TEST_SUBJECT_REGISTRATION
        )
        self.assertGreaterEqual(len(m.output), 1)

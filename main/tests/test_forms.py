from django.test import TestCase
from django.core import mail

from main import forms


class TestForm(TestCase):
    TEST_SUBJECT = "Site message"
    TEST_MESSAGE = "Hi there"

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

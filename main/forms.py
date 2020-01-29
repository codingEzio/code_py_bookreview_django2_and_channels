from django import forms
from django.core.mail import send_mail

import logging
from os import getenv


logger = logging.getLogger(__name__)


class ContactForm(forms.Form):
    name = forms.CharField(label="Your name", max_length=100)
    message = forms.CharField(max_length=600, widget=forms.Textarea)

    def send_mail(self):
        logger.info("Sending email to customer service..")

        message = (
            f"From:"
            f"{self.cleaned_data['name']}\n"
            f"{self.cleaned_data['message']}"
        )
        send_mail(
            subject="Site message",
            message=message,
            from_email=getenv("EMAIL_ADMIN"),
            recipient_list=[getenv("EMAIL_CUSTOMER_SERVICE")],
            fail_silently=False,
        )

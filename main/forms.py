import logging
from os import getenv

from django import forms
from django.core.mail import send_mail
from django.contrib.auth.forms import (
    UserCreationForm as DjangoUserCreationForm,
    UsernameField,
)

from . import models


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


class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        """
        This inner Meta class needs to be overriden when there is a custom User
        model implemented (quote).
        """
        model = models.User
        fields = ("email",)
        field_classes = {"email": UsernameField}

    def send_mail(self):
        logger.info(
            f"Sending signup email for email={self.cleaned_data['email']}"
        )

        message = f"Welcome {self.cleaned_data['email']}"
        send_mail(
            subject="Welcome to Booktime",
            message=message,
            from_email=getenv("EMAIL_ADMIN"),
            recipient_list=[self.cleaned_data["email"]],
            fail_silently=True,
        )
